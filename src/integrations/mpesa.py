from mpesa_python_daraja import mpesa
from config import Config

def initialize_mpesa():
    mpesa.configure(
        consumer_key=Config.MPESA_CONSUMER_KEY,
        consumer_secret=Config.MPESA_CONSUMER_SECRET,
        environment='sandbox'  # or 'production'
    )

def process_mpesa_withdrawal(phone: str, amount: float):
    response = mpesa.stk_push(
        phone_number=phone,
        amount=amount,
        account_reference="CryptoGameBot",
        transaction_desc="Game rewards withdrawal"
    )
    return response