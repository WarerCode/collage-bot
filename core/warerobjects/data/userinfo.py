"""

"""

import enum

import core.warerobjects.warerobject as warer


#TODO: пока что черновик
class UserInfo(warer.WarerObject):
    """

    """

    class Fields(enum.Enum):
        """

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
                 username: str,
                 age: int | None=None):
        """
        Инициализирует self.
        """
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.age = age

    def __repr__(self):
        """
        Возвращает отладочное представление данных.
        """
        return (f"MetaData(hints={self.hints}, "
                f"user_id={self.user_id}, "
                f"username={self.username}, "
                f"age={self.age})")

    def __str__(self):
        """
        Возвращает читаемое строковое представление данных.
        """
        return (f"(hints={self.hints}, "
                f"user_id={self.user_id}, "
                f"username={self.username}, "
                f"age={self.age})")

    def to_dict(self):
        """
        Возвращает представление данных в виде json.
        """
        return {
            "hints": self.hints,
            "user_id": self.user_id,
            "username": self.username,
            "age": self.age
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
    userinfo = UserInfo(1234567890, "Данила", 20)
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
