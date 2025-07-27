from mpesa.api import MpesaEnvironment, Mpesa
from config import Config

def initialize_mpesa():
    env = MpesaEnvironment(
        sandbox=True,  # Set to False for production
        consumer_key=Config.MPESA_CONSUMER_KEY,
        consumer_secret=Config.MPESA_CONSUMER_SECRET
    )
    return Mpesa(env)

def process_mpesa_withdrawal(phone: str, amount: float):
    mpesa = initialize_mpesa()
    return mpesa.stk_push(
        phone_number=phone,
        amount=amount,
        account_reference="CryptoGameBot",
        transaction_desc="Game rewards withdrawal"
    )