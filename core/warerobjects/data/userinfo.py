"""
Класс для хранения данных о пользователе.

Предоставляет интерфейс для хранения стандартных полей пользователя Telegram.
Поля описаны во вложеном перечислителе, рекомендуется использовать.
"""

import enum
import time

import core.warerobjects.warerobject as warer


class UserFields(enum.Enum):
    """
    Перечислитель, хранящий поля пользователя бота.
    """
    USER_ID = "user_id"
    USERNAME = "username"
    IS_BOT = "is_bot"
    STATUS = "status"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    LANGUAGE_CODE = "language_code"
    IS_PREMIUM = "is_premium"
    FREE_COLLAGES_REMAINING = "free_collages_remaining"
    LAST_COLLAGE_DATE = "last_collage_date"
    UPDATED_AT = "updated_at"
    CREATED_AT = "created_at"

    def __str__(self):
        """
        Метод для конвертации перечисления в строку.
        """
        return self.value

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

    def __init__(self, **kwargs):
        """
        Инициализирует self.
        Для гибкости в качестве имен атрибутов используются
        значения перечислителя. Поэтому доступ к ним организуется
        через встроенные методы: __getattrib__ & __setattrib__
        """
        super().__init__()
        for field in UserFields:
            setattr(self,
                    field.value,
                    kwargs.get(field.value, None))

    def __repr__(self):
        """
        Возвращает отладочное представление данных.
        """
        user_fields = ', '.join(
            [f"{key}={value}" for key, value in self.__dict__.items()]
        )
        return f"UserInfo(hints={self.hints}, {user_fields})"

    def __str__(self):
        """
        Возвращает читаемое строковое представление данных.
        """
        user_fields = ', '.join(
            [f"{key}={value}" for key, value in self.__dict__.items()]
        )
        return f"UserInfo(hints={self.hints}, {user_fields})"

    def to_dict(self):
        """
        Возвращает представление данных в виде json.
        """
        return self.__dict__

    def __reset_state(self):
        """
        Сбрасывает состояние объекта до неопределенного.
        Вызывает родительский метод сброса и дополняет его.
        """
        warer.WarerObject.reset_hints(self)
        for attrib, _ in self.__dict__.items():
            setattr(self, attrib, None)

    def update_timestamp(self):
        """

        """
        self.__setattr__(UserFields.UPDATED_AT.value, time.time())



if __name__ == "__main__":
    print("Класс UserInfo для хранения самой важной информации о пользователе")
    help(UserInfo)

    print("\nПример использования класса UserInfo:")
    userinfo = UserInfo(
        user_id=1234567890,
        username="Данила"
    )
    print(userinfo)
    print()

    print("Добавим поля: ")
    userinfo.set_hint(UserFields.STATUS, "онлайн")
    userinfo.set_hint("прошел_опрос", False)
    print(userinfo)
    print()

    print("Вид словаря:")
    print(userinfo.to_dict())
    print()

    print("Сбросим состояние объекта:")
    userinfo.__reset_state()
    print(userinfo)
