import requests
import logging
import os

logger = logging.getLogger(__name__)

def to_xno(raw_amount: int) -> float:
    """Convert raw amount to XNO"""
    return raw_amount / 10**30

def to_raw(xno_amount: float) -> int:
    """Convert XNO to raw amount"""
    return int(xno_amount * 10**30)

def usd_to_xno(amount: float, inverse=False) -> float:
    """Convert between USD and XNO using CoinMarketCap"""
    # In production, use CoinMarketCap API
    # For this example, use a fixed rate
    conversion_rate = 2.5  # 1 XNO = $2.50
    
    if inverse:
        # Convert USD to XNO
        return amount / conversion_rate
    else:
        # Convert XNO to USD
        return amount * conversion_rate