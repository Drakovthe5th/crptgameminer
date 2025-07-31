import hmac
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

def validate_telegram_hash(init_data, raw_data, bot_token):
    """
    Validate Telegram MiniApp hash
    Based on: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        # Parse initData into key-value pairs
        from urllib.parse import parse_qs
        data_dict = parse_qs(init_data)
        
        # Extract hash and remove it from the data
        received_hash = data_dict.get('hash', [''])[0]
        if not received_hash:
            return False
        
        # Create data check string
        data_pairs = []
        for key, values in data_dict.items():
            if key == 'hash':
                continue
            for value in values:
                data_pairs.append(f"{key}={value}")
        data_pairs.sort()
        data_string = "\n".join(data_pairs)
        
        # Compute secret key
        secret_key = hmac.new(
            key=b"WebAppData", 
            msg=bot_token.encode(), 
            digestmod=hashlib.sha256
        ).digest()
        
        # Compute hash
        computed_hash = hmac.new(
            key=secret_key,
            msg=data_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return computed_hash == received_hash
    except Exception as e:
        logger.error(f"Telegram hash validation error: {str(e)}")
        return False