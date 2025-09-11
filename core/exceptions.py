"""
Модуль содержит определения исключений проекта WarerCode.
"""

#TODO:  дописать классы исключений

class WarerError(Exception):
    """
    Базовый класс исключения в проекте WarerCode.

    Родители:
        Exception
    """

    def __init__(self, what: str):
        """
        Инициализирует self.
        """
        super().__init__(what)

if __name__ == "__main__":
    help(WarerError) 

    print("тестовый выброс исключения.")
    try:
        raise WarerError("тестовое исключение.")

    except WarerError as e:
        print(e)
