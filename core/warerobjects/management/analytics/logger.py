"""
Модуль описывает два объекта логгера.

info_logger - для уведомлений и аналитики. Записывает в info.log
error_logger - для ошибок и исключений. Записывает в error.log
"""

import logging


# Логгер для статистики (удачные диалоги)
info_logger = logging.getLogger('info_logger')
info_logger.setLevel(logging.INFO)

# Обработчик для info_logger - пишет в файл info.log
info_handler = logging.FileHandler('info.log')
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(info_formatter)
info_logger.addHandler(info_handler)


# Логгер для ошибок
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)

# Обработчик для error_logger — пишет в файл error.log
error_handler = logging.FileHandler('error.log')
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)



if __name__ == "__main__":
    """
    пример использования:
    info_logger.log("info message...")
    error_logger.log("issue message...")
    """

    print("Справка об объекте инфо логгера:")
    help(info_logger)

    print("Справка об объекте логгера ошибок:")
    help(error_logger)
