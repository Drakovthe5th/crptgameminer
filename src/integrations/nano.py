import logging
from nanopy import Key, Account  # Make sure to import Key
from config import config

logger = logging.getLogger(__name__)
hot_wallet = None

def initialize_nano_wallet(seed: str, representative: str):
    global hot_wallet
    try:
        # Create key from seed first
        key = Key(seed=seed, index=0)
        hot_wallet = Account(key)
        hot_wallet.representative = representative
        logger.info(f"Nano wallet initialized with representative: {representative}")
        logger.info(f"Wallet address: {hot_wallet.account_address}")
    except Exception as e:
        logger.error(f"Error initializing Nano wallet: {e}")

def get_wallet_address() -> str:
    try:
        if hot_wallet:
            return hot_wallet.account_address
        else:
            logger.error("Nano wallet not initialized")
            return ""
    except Exception as e:
        logger.error(f"Error getting wallet address: {e}")
        return ""
    
def send_transaction(destination: str, amount: int) -> str:
    global hot_wallet
    if not hot_wallet:
        raise RuntimeError("Nano wallet not initialized")
    
    try:
        # Create and process send block
        send_block = hot_wallet.send(destination, amount)
        return send_block.hash
    except Exception as e:
        logger.error(f"Error sending transaction: {e}")
        raise