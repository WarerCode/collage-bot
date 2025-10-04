"""
Модуль содержит определения исключений проекта WarerCode.
"""

#TODO:  дописать классы исключений

class WarerError(Exception):
    """
    Базовое исключение для всех ошибок проекта WarerCode — телеграм-бота для создания коллажей.

    Родители:
        Exception
    """

    def __init__(self, what: str):
        """
        Инициализирует self.
        """
        super().__init__(what)


class AnswerError(WarerError):
    """
    Ошибка, связанная с формированием или обработкой ответов бота.

    Родители:
        WarerError
        Exception
    """

    def __init__(self, what: str):
        """
        Инициализирует self.
        """
        super().__init__(what)


class DialogBranchError(WarerError):
    """
    Ошибка при управлении ветвлениями диалога с пользователем.

    Родители:
        WarerError
        Exception
    """

    def __init__(self, what: str):
        """
        Инициализирует self.
        """
        super().__init__(what)


class CollageBuildingError(AnswerError):
    """
    Ошибка, возникающая при сборке или генерации коллажа.

    Родители:
        AnswerError
        WarerError
        Exception
    """

    def __init__(self, what: str):
        """
        Инициализирует self.
        """
        super().__init__(what)


class ContentError(AnswerError):
    """
    Ошибка, связанная с некорректным или отсутствующим содержимым в ответах.

    Родители:
        AnswerError
        WarerError
        Exception
    """

    def __init__(self, what: str):
        """
        Инициализирует self.
        """
        super().__init__(what)


class AccessError(WarerError):
    """
    Ошибка, возникающая при проблемах с доступом или правами пользователя.

    Родители:
        WarerError
        Exception
    """

    def __init__(self, what: str):
        """
        Инициализирует self.
        """
        super().__init__(what)



if __name__ == "__main__":
    help(WarerError) 

    print("тестовый выброс исключений.")
    errors = [
        WarerError,
        DialogBranchError,
        CollageBuildingError,
        AccessError,
        ContentError,
        AnswerError
    ]

    for err in errors:
        try:
            raise err(f"тестовое исключение: {err.__name__}")

        except WarerError as e:
            print(e)
