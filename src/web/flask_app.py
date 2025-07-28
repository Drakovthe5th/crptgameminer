from flask import Flask
from src.web.routes import configure_routes

def create_app():
    app = Flask(__name__)
    configure_routes(app)
    return app