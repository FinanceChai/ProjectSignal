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
                    pair_info = f"""
Chain ID: {pair['chainId']}
DEX ID: {pair['dexId']}
URL: {pair['url']}
Pair Address: {pair['pairAddress']}
Base Token: {pair['baseToken']['name']} ({pair['baseToken']['symbol']})
Quote Token: {pair['quoteToken']['symbol']}
Price (Native): {pair['priceNative']}
Price (USD): {pair.get('priceUsd', 'N/A')}
Volume (24h): {pair['volume']['h24']}
Liquidity (USD): {pair['liquidity'].get('usd', 'N/A')}
Pair Created At: {pair['pairCreatedAt']}
"""
                    if 'info' in pair:
                        info = pair['info']
                        if 'websites' in info:
                            for website in info['websites']:
                                pair_info += f"\nWebsite: {website['url']}"
                        if 'socials' in info:
                            for social in info['socials']:
                                if social['type'] == 'twitter':
                                    pair_info += f"\nTwitter: {social['url']}"
                                elif social['type'] == 'telegram':
                                    pair_info += f"\nTelegram: {social['url']}"
                    await update.message.reply_text(pair_info)
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
