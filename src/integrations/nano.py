from nanopy import Account
from config import config

hot_wallet = None

def initialize_nano_wallet(seed: str, representative: str):
    global hot_wallet
    hot_wallet = Account(seed, 0)
    hot_wallet.representative = representative

def get_wallet_balance() -> int:
    return hot_wallet.balance

def send_transaction(destination: str, amount_raw: int) -> str:
    return hot_wallet.send(destination, amount_raw)

def get_wallet_address() -> str:
    # Corrected attribute name
    return hot_wallet.account_address