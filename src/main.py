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
    initialize_paypal()
    
    # Start background services
    threading.Thread(target=start_faucet_scheduler, daemon=True).start()
    
    # Set up Telegram bot
    application = Application.builder().token(Config.TOKEN).build()
    setup_handlers(application)
    
    # Start the bot
    application.run_polling()