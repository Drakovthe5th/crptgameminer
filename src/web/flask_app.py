from flask import Flask, request, jsonify, render_template
from src.web.routes import configure_routes
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    configure_routes(app)
    return app