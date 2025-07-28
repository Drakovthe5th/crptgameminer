from pypesa import MPESA
from config import Config
import base64
import json
import os

def initialize_mpesa():
    # Create keys.json dynamically from environment variables
    keys = {
        'api_key': Config.MPESA_CONSUMER_KEY,
        'public_key': Config.MPESA_PUBLIC_KEY
    }
    
    # Save to keys.json
    with open('keys.json', 'w') as f:
        json.dump(keys, f)
    
    # Initialize MPESA client
    environment = "sandbox" if Config.MPESA_SANDBOX else "production"
    return MPESA(environment=environment)

def process_mpesa_withdrawal(phone: str, amount: float):
    mpesa = initialize_mpesa()
    
    # Prepare transaction data
    transaction = {
        "input_Amount": str(amount),
        "input_Country": "KEN",  # Kenya
        "input_Currency": "KES", # Kenyan Shillings
        "input_CustomerMSISDN": phone,
        "input_ServiceProviderCode": Config.MPESA_SHORTCODE,
        "input_ThirdPartyConversationID": "cryptogame_" + os.urandom(8).hex(),
        "input_TransactionReference": "CRYPTO_" + os.urandom(4).hex(),
        "input_PurchasedItemsDesc": "Crypto Rewards"
    }
    
    # Process C2B transaction
    return mpesa.customer_to_bussiness(transaction)