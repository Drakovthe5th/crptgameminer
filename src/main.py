import os
import threading
import asyncio
from telegram.ext import Application
from src.database.firebase import initialize_firebase
from src.integrations.nano import initialize_nano_wallet
from src.features.faucets import start_faucet_scheduler
from src.telegram.setup import setup_handlers
from config import config

# Global application reference
application = None

def run_bot():
    global application
    
    # Initialize services
    initialize_firebase(config.FIREBASE_CREDS)
    initialize_nano_wallet(config.NANO_SEED, config.REPRESENTATIVE)
    
    # Start background services
    threading.Thread(target=start_faucet_scheduler, daemon=True).start()
    
    # Set up Telegram bot
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    setup_handlers(application)
    
    # Configure based on environment
    if config.ENV == 'production':
        # Proper async webhook setup
        asyncio.run(set_webhook())
    else:
        # Polling mode for development
        application.run_polling()
        print("Bot started in polling mode")

async def set_webhook():
    """Async function to set webhook properly"""
    await application.bot.set_webhook(
        url=f"https://{config.RENDER_URL}/{config.TELEGRAM_TOKEN}"
    )
    print(f"Webhook set: https://{config.RENDER_URL}/{config.TELEGRAM_TOKEN}")