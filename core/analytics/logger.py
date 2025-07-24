import logging

logging.basicConfig(
    level=logging.DEBUG,  # logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()  # вывод в консоль
    ]
)

# using logger global
logger = logging.getLogger(__name__)

# initial message
logger.info("logger initialized")
