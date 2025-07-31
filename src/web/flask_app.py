from flask import Flask
from src.web.routes import configure_routes
from google.cloud import secretmanager
import os
import logging
import json

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_name, project_id):
    """Retrieve secrets from Google Secret Manager"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Error accessing secret {secret_name}: {str(e)}")
        return os.getenv(secret_name.upper(), "")  # Fallback to environment variable

def create_app():
    app = Flask(__name__)
    
    # Get GCP project ID
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        logger.info("GOOGLE_CLOUD_PROJECT not set, trying metadata server")
        try:
            import requests
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
            headers = {'Metadata-Flavor': 'Google'}
            project_id = requests.get(metadata_url, headers=headers, timeout=2).text
        except Exception:
            project_id = "crypto-miner-bot"  # Fallback
            logger.warning(f"Using fallback project ID: {project_id}")
    
    # Load configuration from secrets
    app.config['TELEGRAM_TOKEN'] = get_secret('telegram-token', project_id)
    app.config['FIREBASE_CREDS'] = get_secret('firebase-creds', project_id)
    app.config['NANO_SEED'] = get_secret('nano-seed', project_id)
    
    # Parse Firebase credentials
    try:
        firebase_creds = json.loads(app.config['FIREBASE_CREDS'])
        app.config['FIREBASE_CONFIG'] = firebase_creds
    except Exception as e:
        logger.error(f"Error parsing Firebase credentials: {str(e)}")
    
    # Set other config values
    app.config['ENVIRONMENT'] = os.getenv('ENVIRONMENT', 'production')
    app.config['MIN_WITHDRAWAL'] = 0.1  # Minimum withdrawal in XNO
    app.config['AD_REWARD_AMOUNT'] = 0.005  # Base ad reward amount
    
    # Configure routes
    configure_routes(app)
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; frame-src 'self' https://telegram.org;"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    if not app.debug and os.getenv("WERKZEUG_RUN_MAIN") != "true":
        from src.main import run_bot
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()

    return app

# Create application instance
app = create_app()

#if __name__ == "__main__":
 #   app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)), debug=app.config['ENVIRONMENT'] == 'development')

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))