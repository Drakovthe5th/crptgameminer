import schedule
import time
import requests
from src.integrations.nano import get_wallet_address
from config import Config

def claim_from_faucets():
    faucets = [
        f"https://faucet.zenofnano.com/claim?address={get_wallet_address()}",
        f"https://nanodrop.io/claim.php?address={get_wallet_address()}",
        f"https://free-nano.com/claim.php?address={get_wallet_address()}"
    ]
    
    for url in faucets:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                print(f"Claimed from {url}")
        except Exception as e:
            print(f"Faucet claim failed ({url}): {str(e)}")

def start_faucet_scheduler():
    # Run immediately on start
    claim_from_faucets()
    
    # Schedule regular claims
    schedule.every(4).hours.do(claim_from_faucets)
    
    while True:
        schedule.run_pending()
        time.sleep(60)