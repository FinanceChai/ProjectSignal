import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Get the Telegram bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Define the API base URL
API_BASE_URL = "https://api.dexscreener.com/latest/dex/search?q="

# Function to calculate buy/sell ratio
def calculate_ratio(buys, sells):
    if sells == 0:
        return "N/A" if buys == 0 else f"{buys:.1f}x"
    return f"{(buys / sells):.1f}x"

# Function to format USD values without decimals
def format_usd(value):
    return f"${value:,.0f}"

# Function to search for token information
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        contract_address = context.args[0]
        url = f"{API_BASE_URL}{contract_address}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])
            if pairs:
                for pair in pairs:
                    txns = pair.get('txns', {})
                    buys_h1 = txns.get('h1', {}).get('buys', 0)
                    sells_h1 = txns.get('h1', {}).get('sells', 0)
                    buys_h6 = txns.get('h6', {}).get('buys', 0)
                    sells_h6 = txns.get('h6', {}).get('sells', 0)
                    buys_h24 = txns.get('h24', {}).get('buys', 0)
                    sells_h24 = txns.get('h24', {}).get('sells', 0)
                    
                    pair_info = f"""
Token: {pair['baseToken']['name']} ({pair['baseToken']['symbol']})

<a href="{pair['url']}">DexScreener</a> + <a href="https://rugcheck.xyz/tokens/{contract_address}">Rugcheck</a> + <a href="app.bubblemaps.io/sol/{contract_address}">BubbleMaps</a>

Overview
Price (USD): {pair.get('priceUsd', 'N/A')}
FDV: {format_usd(pair.get('fdv', 0))}
Liquidity (USD): {format_usd(pair['liquidity'].get('usd', 0))}

Buy / Sell Ratios
B/S Ratio (1h): {calculate_ratio(buys_h1, sells_h1)}
B/S Ratio (6h): {calculate_ratio(buys_h6, sells_h6)}
B/S Ratio (24h): {calculate_ratio(buys_h24, sells_h24)}

Trading Volumes
Volume (1h): {format_usd(pair['volume']['h1'])}
Volume (6h): {format_usd(pair['volume']['h6'])}
Volume (24h): {format_usd(pair['volume']['h24'])}
"""
                    await update.message.reply_text(pair_info, parse_mode='HTML')
            else:
                await update.message.reply_text("No pairs found for the given contract address.")
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    else:
        await update.message.reply_text("Please provide a contract address. Usage: /search <contract address>")

def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handler for /search
    application.add_handler(CommandHandler('search', search))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
