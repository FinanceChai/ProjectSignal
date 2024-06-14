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
                    buys_h6 = txns.get('h6', {}).get('buys', 0
