import os
import threading
from telegram.ext import Application
from src.database.firebase import initialize_firebase
from src.integrations.nano import initialize_nano_wallet
from src.features.faucet import start_faucet_scheduler
from src.telegram.setup import setup_handlers
from config import Config

def run_bot():
    # Initialize services
    initialize_firebase(Config.FIREBASE_CREDS)
    initialize_nano_wallet(Config.NANO_SEED, Config.REPRESENTATIVE)
    # initialize_paypal()  # Uncomment if needed
    
    # Start background services
    threading.Thread(target=start_faucet_scheduler, daemon=True).start()
    
    # Set up Telegram bot
    application = Application.builder().token(Config.TOKEN).build()
    setup_handlers(application)
    
    # Get environment variables for webhook
    PORT = int(os.getenv('PORT', 10000))
    RENDER_URL = os.getenv('RENDER_EXTERNAL_URL', Config.RENDER_URL)
    
    if Config.ENV == 'production':
        # Webhook mode for production
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"https://{RENDER_URL}/{Config.TOKEN}",
            url_path=Config.TOKEN
        )
        print(f"Bot started in webhook mode: https://{RENDER_URL}/{Config.TOKEN}")
    else:
        # Polling mode for development
        application.run_polling()
        print("Bot started in polling mode")