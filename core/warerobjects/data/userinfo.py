"""
Класс для хранения данных о пользователе.

Предоставляет интерфейс для хранения стандартных полей пользователя Telegram.
Поля описаны во вложеном перечислителе, рекомендуется использовать.
"""

import enum

import core.warerobjects.warerobject as warer


class UserInfo(warer.WarerObject):
    """
    Класс для хранения данных о пользователе Telegram.

    Родители:
        warer.WarerObject
        abc.ABC

    Аттрибуты:
        user_id (int): уникальный внутренний идентификатор пользователя Telegram.
        username (str):  имя пользователя.
    """

    class Fields(enum.Enum):
        """
        Класс-перечислитель для унификации стандартных полей
        пользователя Telegram.
        """

        FIRST_NAME = "first_name"
        LAST_NAME = "last_name"
        USERNAME = "username"
        ID = "id"
        PHONE = "phone"
        PHOTO = "photo"
        STATUS = "status"
        LANG_CODE = "lang_code"
        IS_VERIFIED = "is_verified"
        IS_PREMIUM = "is_premium"
        ABOUT = "about"

    def __init__(self,
                 user_id,
                 username: str):
        """
        Инициализирует self.
        """
        super().__init__()
        self.user_id = user_id
        self.username = username

    def __repr__(self):
        """
        Возвращает отладочное представление данных.
        """
        return (f"MetaData(hints={self.hints}, "
                f"id={self.user_id}, "
                f"username={self.username})")

    def __str__(self):
        """
        Возвращает читаемое строковое представление данных.
        """
        return (f"UserInfo(hints={self.hints}, "
                f"id={self.user_id}, "
                f"username={self.username})")

    def to_dict(self):
        """
        Возвращает представление данных в виде json.
        """
        return {
            "hints": self.hints,
            "id": self.user_id,
            "username": self.username
        }

    def reset_state(self):
        """
        Сбрасывает состояние объекта до состояния по умолчанию.
        Вызывает родительский метод сброса и дополняет его.
        """
        warer.WarerObject.reset_hints(self)
        self.user_id = None
        self.username = None



if __name__ == "__main__":
    print("Класс UserInfo для хранения самой важной информации о пользователе")
    help(UserInfo)

    print("Пример использования класса UserInfo:")
    userinfo = UserInfo(1234567890, "Данила")
    print(userinfo)
    print()

    print("Добавим поля: ")
    userinfo.set_hint(UserInfo.Fields.STATUS, "онлайн")
    userinfo.set_hint("прошел_опрос", False)
    print(userinfo)
    print()

    print("Вид словаря:")
    print(userinfo.to_dict())
    print()

    print("Сбросим состояние объекта:")
    userinfo.reset_state()
    print(userinfo)
