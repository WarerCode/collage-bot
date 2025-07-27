import logging
from dotenv import load_dotenv
import os

load_dotenv('config.env')

ANALYTICS_ROOT = os.getenv('ANALYTICS_ROOT')
LOG_PATH = os.path.join(ANALYTICS_ROOT, 'bot.log')

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Logger initialized")
