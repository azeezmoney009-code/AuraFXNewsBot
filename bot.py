import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.first_name
    welcome_text = (
        f"Hello {user}! 👋\n\n"
        "Welcome to **Finnhub Market Bot**! 📈\n"
        "Send /news to get live market and Forex news powered by Finnhub."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# /news command fetching from Finnhub API
async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🔎 Fetching news from Finnhub...")

    finnhub_key = os.getenv("FINNHUB_API_KEY")
    if not finnhub_key:
        await update.message.reply_text("⚠️ FINNHUB_API_KEY is missing in environment variables.")
        return

    try:
        # Finnhub general/forex news endpoint
        url = f"https://finnhub.io/api/v1/news?category=forex&token={finnhub_key}"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Extract top 3 articles
        articles = data[:3] if isinstance(data, list) else []

        if not articles:
            await update.message.reply_text("No recent news found at the moment.")
            return

        for item in articles:
            headline = item.get("headline", "No Title")
            source = item.get("source", "Finnhub")
            url_link = item.get("url", "")

            message = f"📰 *{headline}*\nSource: _{source}_\n🔗 [Read Story]({url_link})"
            await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error calling Finnhub API: {e}")
        await update.message.reply_text("⚠️ Failed to fetch news. Please try again later.")

# Auto-reply for regular messages
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Type /news to fetch live Finnhub market updates!")

def main() -> None:
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        raise ValueError("TELEGRAM_TOKEN environment variable is missing!")

    app = Application.builder().token(telegram_token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    print("Finnhub Telegram Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
