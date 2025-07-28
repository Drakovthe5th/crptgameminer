import logging
from nanopy import Account
from config import config

logger = logging.getLogger(__name__)
hot_wallet = None

def initialize_nano_wallet(seed: str, representative: str):
    global hot_wallet
    try:
        hot_wallet = Account(seed, 0)
        hot_wallet.representative = representative
        logger.info(f"Nano wallet initialized with representative: {representative}")
    except Exception as e:
        logger.error(f"Error initializing Nano wallet: {e}")

def get_wallet_address() -> str:
    try:
        # Try both common attribute names
        if hasattr(hot_wallet, 'account_address'):
            return hot_wallet.account_address
        elif hasattr(hot_wallet, 'address'):
            return hot_wallet.address
        else:
            logger.error("Nano wallet object has no address attribute")
            return ""
    except Exception as e:
        logger.error(f"Error getting wallet address: {e}")
        return ""