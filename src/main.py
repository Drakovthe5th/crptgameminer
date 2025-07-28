import os
import threading
from telegram.ext import Application
from src.database.firebase import initialize_firebase
from src.integrations.nano import initialize_nano_wallet
from src.features.faucet import start_faucet_scheduler
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
        # Set webhook for production
        application.bot.set_webhook(
            url=f"https://{config.RENDER_URL}/{config.TELEGRAM_TOKEN}"
        )
        print(f"Webhook set: https://{config.RENDER_URL}/{config.TELEGRAM_TOKEN}")
    else:
        # Polling mode for development
        application.run_polling()
        print("Bot started in polling mode")