import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import secretmanager
import logging
import json
import os

logger = logging.getLogger(__name__)

# Initialize Firebase app
app = None
db = None

def initialize_firebase(config):
    global app, db
    try:
        # Check if already initialized
        if app is not None:
            return db
        
        # Initialize with provided config
        cred = credentials.Certificate(config)
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        logger.info("Firebase initialized successfully")
        return db
    except Exception as e:
        logger.error(f"Firebase initialization error: {str(e)}")
        raise

def get_user_ref(user_id):
    if db is None:
        raise Exception("Firebase not initialized")
    return db.collection('users').document(str(user_id))

def get_user_data(user_id):
    doc = get_user_ref(user_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

def get_user_balance(user_id):
    user_data = get_user_data(user_id)
    return user_data.get('balance', 0) if user_data else 0

def update_balance(user_id, amount):
    user_ref = get_user_ref(user_id)
    
    # Create user if doesn't exist
    if not user_ref.get().exists:
        user_ref.set({
            'balance': 0.0,
            'created_at': firestore.SERVER_TIMESTAMP
        })
    
    # Update balance
    new_balance = max(0, get_user_balance(user_id) + amount)
    user_ref.update({'balance': new_balance})
    return new_balance

def create_user(user_id, username):
    user_ref = get_user_ref(user_id)
    if not user_ref.get().exists:
        user_ref.set({
            'username': username,
            'balance': 0.0,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_played': {}
        })