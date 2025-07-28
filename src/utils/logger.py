import logging
import os

def setup_logger():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log_level
    )
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logger()