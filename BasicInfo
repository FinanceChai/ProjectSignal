import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Load environment variables from .env file
load_dotenv()

# Get the Telegram bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Define the states for the conversation
ENTER_ADDRESS = 1

# Define the API base URL
API_BASE_URL = "https://api.dexscreener.com/latest/dex/search?q="

# Start command handler
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Welcome to the DEX Screener bot! Please enter the contract address of the token you want to search for.')
    return ENTER_ADDRESS

# Function to search for token information
def search(update: Update, context: CallbackContext) -> int:
    contract_address = update.message.text
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
                update.message.reply_text(pair_info)
        else:
            update.message.reply_text("No pairs found for the given contract address.")
    else:
        update.message.reply_text(f"Error: {response.status_code}")

    return ConversationHandler.END

# Cancel command handler
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Search cancelled.')
    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTER_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, search)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
