import logging

logging.basicConfig(
    level=logging.DEBUG,  # logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analytics/bot.log", encoding='utf-8'),
        logging.StreamHandler()  # console output
    ]
)

# using logger global
LOGGER = logging.getLogger(__name__)

# initial message
LOGGER.info("logger initialized")
