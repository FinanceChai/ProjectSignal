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

# Function to extract Twitter handle from URL
def extract_twitter_handle(url):
    if "twitter.com" in url:
        return url.split("/")[-1]
    return None

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
                total_liquidity = 0
                total_volume_h1 = 0
                total_volume_h6 = 0
                total_volume_h24 = 0
                total_buys_h1 = 0
                total_sells_h1 = 0
                total_buys_h6 = 0
                total_sells_h6 = 0
                total_buys_h24 = 0
                total_sells_h24 = 0
                base_token_name = pairs[0]['baseToken']['name']
                base_token_symbol = pairs[0]['baseToken']['symbol']
                dex_url = pairs[0]['url']
                rugcheck_url = f"https://rugcheck.xyz/{contract_address}"
                bubblemaps_url = f"http://app.bubblemaps.io/sol/{contract_address}"
                twitter_handle = None

                for pair in pairs:
                    if 'info' not in pair:
                        continue

                    liquidity = pair.get('liquidity', {}).get('usd', 0)
                    volume_h1 = pair.get('volume', {}).get('h1', 0)
                    volume_h6 = pair.get('volume', {}).get('h6', 0)
                    volume_h24 = pair.get('volume', {}).get('h24', 0)
                    txns = pair.get('txns', {})

                    buys_h1 = txns.get('h1', {}).get('buys', 0)
                    sells_h1 = txns.get('h1', {}).get('sells', 0)
                    buys_h6 = txns.get('h6', {}).get('buys', 0)
                    sells_h6 = txns.get('h6', {}).get('sells', 0)
                    buys_h24 = txns.get('h24', {}).get('buys', 0)
                    sells_h24 = txns.get('h24', {}).get('sells', 0)

                    total_liquidity += liquidity
                    total_volume_h1 += volume_h1
                    total_volume_h6 += volume_h6
                    total_volume_h24 += volume_h24
                    total_buys_h1 += buys_h1
                    total_sells_h1 += sells_h1
                    total_buys_h6 += buys_h6
                    total_sells_h6 += sells_h6
                    total_buys_h24 += buys_h24
                    total_sells_h24 += sells_h24

                    if 'socials' in pair['info']:
                        for social in pair['info']['socials']:
                            if social["type"].lower() == "twitter" and not twitter_handle:
                                twitter_handle = extract_twitter_handle(social["url"])

                pair_info = f"""
Token: {base_token_name} ({base_token_symbol})

<a href="{dex_url}">DexScreener</a> + <a href="{rugcheck_url}">Rugcheck</a> + <a href="{bubblemaps_url}">BubbleMaps</a>

Overview
Price (USD): {pairs[0].get('priceUsd', 'N/A')}
FDV: {format_usd(pairs[0].get('fdv', 0))}
Liquidity (USD): {format_usd(total_liquidity)}

Buy / Sell Ratios
B/S Ratio (1h): {calculate_ratio(total_buys_h1, total_sells_h1)}
B/S Ratio (6h): {calculate_ratio(total_buys_h6, total_sells_h6)}
B/S Ratio (24h): {calculate_ratio(total_buys_h24, total_sells_h24)}

Trading Volumes
Volume (1h): {format_usd(total_volume_h1)}
Volume (6h): {format_usd(total_volume_h6)}
Volume (24h): {format_usd(total_volume_h24)}
"""
                if 'websites' in pairs[0]['info']:
                    pair_info += "\n"
                    for site in pairs[0]['info']['websites']:
                        pair_info += f'<a href="{site["url"]}">{site["label"]}</a> + '

                if twitter_handle:
                    tweetscout_url = f"http://app.tweetscout.io/search?q={twitter_handle}"
                    pair_info += f'<a href="{tweetscout_url}">TweetScout</a>'

                # Remove the trailing " + " if it exists
                if pair_info.endswith(" + "):
                    pair_info = pair_info[:-3]

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
