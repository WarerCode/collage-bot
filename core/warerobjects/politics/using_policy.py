"""
Модуль определяет классы для политики использования с разграничением прав и лимитов пользователей.

Содержит:
- Permission — перечисление прав пользователей.
- UsingPolicy — класс, реализующий политику использования для разных типов пользователей.
- UsingPolicy.UserType — перечисление типов пользователей с соответствующими наборами прав.
"""

import enum

import core.warerobjects.politics.basepolicy as policy
import core.warerobjects.politics.using_limits as using_limits


class Permission(enum.Enum):
    """
    Перечисление доступных разрешений (прав) для пользователей.
    """

    # для смертных пользователей
    UNLIMITED = "unlimited"
    NO_PROMOTIONS = "no_promotions"
    SEND_IMAGES = "send_images"
    CREATE_COLLAGE = "create_collage"
    EDIT_COLLAGE = "edit_collage"
    MORE_EFFECTS = "more_effects"

    # для супер пользователей
    MANAGE_USERS = "manage_users"
    ACCESS_STATS = "access_stats"
    CREATE_POLL = "create_poll"


class UsingPolicy(policy.Policy):
    """
    Класс политики использования с разграничением прав и лимитов.

    Родители:
        policy.Policy
        warer.WarerObject
        abc.ABC

    Атрибуты:
        _usertype (UserType): тип пользователя, определяющий права и лимиты.
        _permissions (list): список прав пользователя.
        _limits (dict): словарь с лимитами для данного типа пользователя.
    """

    class UserType(enum.Enum):
        """
        Типы пользователей с соответствующими правами.
        """

        DEFAULT = [
            Permission.SEND_IMAGES.value,
            Permission.CREATE_COLLAGE.value,
            Permission.EDIT_COLLAGE.value,
        ]
        SUBSCRIBER = [p for p in DEFAULT] + [
            Permission.UNLIMITED.value,
            Permission.NO_PROMOTIONS.value
        ]
        BANNED = []
        ADMIN = [p.value for p in Permission]

    def __init__(self, usertype: UserType):
        """
        Инициализация объекта политики использования.

        Параметры:
            usertype (UserType): тип пользователя, определяющий права и лимиты.
        """
        super().__init__()
        self._usertype = usertype
        self._permissions = usertype.value

        self._limits = {}
        self.__set_limits()

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return (f"UsingPolicy(usertype={self._usertype}, "
                f"permissions={self._permissions}, "
                f"limits={self._limits})")

    def __repr__(self):
        """
        Формальное строковое представление объекта.
        """
        return (f"(usertype={self._usertype}, "
                f"permissions={self._permissions}, "
                f"limits={self._limits})")

    def to_dict(self):
        """
        Представление объекта в виде словаря.
        """
        return {
            "usertype": self._usertype.value,
            "permissions": self._permissions,
            "limits": self._limits
        }

    def get_limits(self):
        """
        Получить текущие лимиты.
        """
        return self._limits

    def __set_limits(self):
        """
        Устанавливает лимиты в зависимости от типа пользователя.
        """
        if self._usertype == UsingPolicy.UserType.DEFAULT:
            self._limits = using_limits.DEFAULT_LIMITS

        elif self._usertype == UsingPolicy.UserType.BANNED:
            self._limits = using_limits.BANNED_LIMITS

        elif self._usertype == UsingPolicy.UserType.SUBSCRIBER:
            self._limits = using_limits.SUBSCRIBER_LIMITS

        elif self._usertype == UsingPolicy.UserType.ADMIN:
            self._limits = using_limits.ADMIN_LIMITS

        else:
            # TODO: сделать свои классы ошибок и здесь выбросить исключение
            raise ValueError("Неизвестный тип пользователя")


if __name__ == "__main__":
    print("Класс политики использования с разграничением прав и лимитов:")
    help(UsingPolicy)

    print("__str__:")
    for user_type in UsingPolicy.UserType:
        using = UsingPolicy(user_type)
        print(f"Политика использования для {user_type.name}: {using}")
    print()

    print("__repr__:")
    for user_type in UsingPolicy.UserType:
        using = UsingPolicy(user_type)
        print(f"Политика использования для {user_type.name}: {using.__repr__()}")
    print()

    print("to_dict:")
    for user_type in UsingPolicy.UserType:
        using = UsingPolicy(user_type)
        print(f"Политика использования для {user_type.name}: {using.to_dict()}")
