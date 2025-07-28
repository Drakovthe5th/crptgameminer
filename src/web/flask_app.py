from flask import Flask
from src.web.routes import configure_routes
from src.telegram.bot import bot, dispatcher  # Import your bot instance

def create_app():
    app = Flask(__name__)
    
    # Initialize routes
    configure_routes(app)
    
    # Initialize bot components
    from src.telegram import setup_handlers
    setup_handlers(dispatcher)
    
    return app