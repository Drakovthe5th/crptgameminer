# config.py
import os

class Config:
    # Firebase
    FIRESTORE_PROJECT = os.getenv("FIRESTORE_PROJECT")
    
    # Nano
    NANO_NODE_URL = os.getenv("NANO_NODE_URL", "https://node.somenano.com/proxy")
    
    # M-Pesa
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
    MPESA_PUBLIC_KEY = os.getenv("MPESA_PUBLIC_KEY")  # New public key
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
    MPESA_SANDBOX = os.getenv("MPESA_SANDBOX", "True") == "True"  # Default to sandbox
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
    PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")  # or "live"
    
    # Withdrawal Settings
    WITHDRAWAL_FEES = {
        'nano': 0.0,
        'mpesa': 0.03,  # 3%
        'equity': 0.02   # 2%
    }