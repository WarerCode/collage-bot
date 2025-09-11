"""
Модуль определяет классы для политики использования с разграничением прав и лимитов пользователей.

Содержит:
- Permission — перечисление прав пользователей.
- UsingPolicy — класс, реализующий политику использования для разных типов пользователей.
- UsingPolicy.UserType — перечисление типов пользователей с соответствующими наборами прав.
"""

import core.warerobjects.politics.basepolicy as policy
import core.warerobjects.politics.using_limits as using_limits


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

    UserType = using_limits.UserType

    def __init__(self, usertype: UserType):
        """
        Инициализация объекта политики использования.

        Параметры:
            usertype (UserType): тип пользователя, определяющий права и лимиты.
        """
        super().__init__()
        self._usertype = usertype.value
        self._limits = using_limits.UsingLimits(user_type)
        self._notify_policy = None

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return (f"UsingPolicy(usertype={self._usertype},"
                f"limits={self._limits},"
                f"notify_policy={self._notify_policy})")

    def __repr__(self):
        """
        Формальное строковое представление объекта.
        """
        return (f"(usertype={self._usertype},"
                f"limits={self._limits},"
                f"notify_policy={self._notify_policy})")

    def to_dict(self):
        """
        Представление объекта в виде словаря.
        """
        return {
            "usertype": self._usertype,
            "limits": self._limits,
            "notify_policy": self._notify_policy
        }

    def get_limits(self):
        """
        Получить текущие лимиты.
        """
        return self._limits



if __name__ == "__main__":
    print("Класс политики использования с разграничением прав и лимитов:")
    help(UsingPolicy)

    UserType = UsingPolicy.UserType

    print("__str__:")
    for user_type in UserType:
        using = UsingPolicy(user_type)
        print(f"Политика использования для {user_type.name}: {using}")
    print()

    print("__repr__:")
    for user_type in UserType:
        using = UsingPolicy(user_type)
        print(f"Политика использования для {user_type.name}: {using.__repr__()}")
    print()

    print("to_dict:")
    for user_type in UserType:
        using = UsingPolicy(user_type)
        print(f"Политика использования для {user_type.name}: {using.to_dict()}")
