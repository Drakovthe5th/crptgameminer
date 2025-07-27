import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

db = None
users_ref = None
quests_ref = None
ads_ref = None

import os
import json
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    cred_json = os.getenv("FIREBASE_CREDS_JSON")
    if not cred_json:
        raise ValueError("Firebase credentials not found in environment")
    
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# User operations
def get_user_ref(user_id: int):
    return users_ref.document(str(user_id))

def get_user_data(user_id: int):
    doc = get_user_ref(user_id).get()
    return doc.to_dict() if doc.exists else None

def create_user(user_id: int, username: str):
    user_ref = get_user_ref(user_id)
    if not user_ref.get().exists:
        user_ref.set({
            'user_id': user_id,
            'username': username,
            'balance': 0.0,
            'points': 0,
            'last_played': None,
            'referral_count': 0,
            'faucet_claimed': None,
            'withdrawal_methods': {},
            'completed_quests': {},
            'created_at': SERVER_TIMESTAMP
        })
    return user_ref

def update_user(user_id: int, update_data: dict):
    get_user_ref(user_id).update(update_data)

def get_user_balance(user_id: int) -> float:
    user_data = get_user_data(user_id)
    return user_data.get('balance', 0.0) if user_data else 0.0

def update_balance(user_id: int, amount: float):
    user_ref = get_user_ref(user_id)
    current_balance = get_user_balance(user_id)
    new_balance = current_balance + amount
    
    if not user_ref.get().exists:
        create_user(user_id, "")
    
    user_ref.update({'balance': new_balance})
    return new_balance

# Leaderboard operations
def update_leaderboard_points(user_id: int, points: int):
    user_ref = get_user_ref(user_id)
    user_ref.update({
        'points': firestore.Increment(points),
        'last_active': SERVER_TIMESTAMP
    })