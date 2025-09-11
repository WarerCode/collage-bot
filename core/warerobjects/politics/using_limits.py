"""
Модуль содержит определения лимитов использования для разных типов пользователей.

Включает словари с ограничениями:
- DEFAULT_LIMITS — лимиты для обычных пользователей.
- SUBSCRIBER_LIMITS — лимиты для подписчиков.
- BANNED_LIMITS — ограничения для заблокированных пользователей.
- ADMIN_LIMITS — специальные права для администраторов.

Класс UsingLimits предоставляет удобный интерфейс для доступа к этим лимитам по типу пользователя.

TODO:
    - @JaneeWatermelon уточнить и согласовать реальные значения лимитов и эффектов.
"""

import enum

import core.warerobjects.warerobject as warer


class UserType(enum.Enum):
    """
    Типы пользователей с соответствующими правами.
    """

    DEFAULT = "default"
    SUBSCRIBER = "subscriber"
    BOT = "bot"
    BANNED = "banned"
    ADMIN = "admin"

class Permission(enum.Enum):
    """
    Перечисление доступных разрешений (прав) для пользователей.
    """

    # для обычных пользователей
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


NO_LIMIT = None


# Атрибуты политики использования
COLLAGES_PER_DAYS = "collages_per_day"
EFFECTS = "effects"
LOADINGS_PER_DAY = "loadings_per_day"
NOTIFY_PERIOD = "notify_period"
PERMISSIONS = "permissions"

# Дефолтные значения эффектов и разрешений
DEFAULT_EFFECTS = ["", "", ""]
EXTENDED_EFFECTS = ["", "", "", ""]
DEFAULT_PERMISSIONS = []
SUBSCRIBE_PERMISSIONS = []
ADMIN_PERMISSIONS = []
BANNED_PERMISSIONS = []


class UsingLimits(warer.WarerObject):
    """
    Класс, представляющий лимиты использования и разрешения для разных типов пользователей.

    Родители:
        warer.WarerObject
        abc.ABC

    Атрибуты класса:
        DEFAULT_LIMITS: Лимиты для обычных пользователей.
        SUBSCRIBER_LIMITS: Лимиты для подписчиков.
        BANNED_LIMITS: Лимиты для заблокированных пользователей.
        ADMIN_LIMITS: Лимиты для администраторов.
        USING_POLITICS_LIMITS: Сопоставление типов пользователей с их лимитами.

    Атрибут экземпляра:
        value: Словарь лимитов для конкретного типа пользователя.
    """

    DEFAULT_LIMITS = {
        COLLAGES_PER_DAYS: 100,
        EFFECTS: DEFAULT_EFFECTS,
        LOADINGS_PER_DAY: 20,
        NOTIFY_PERIOD: 3,
        PERMISSIONS: DEFAULT_PERMISSIONS
    }

    SUBSCRIBER_LIMITS = {
        COLLAGES_PER_DAYS: NO_LIMIT,
        EFFECTS: EXTENDED_EFFECTS,
        LOADINGS_PER_DAY: 100,
        NOTIFY_PERIOD: 7,
        PERMISSIONS: SUBSCRIBE_PERMISSIONS
    }

    BANNED_LIMITS = {
        COLLAGES_PER_DAYS: 0,
        EFFECTS: [],
        LOADINGS_PER_DAY: 0,
        NOTIFY_PERIOD: 2,
        PERMISSIONS: BANNED_PERMISSIONS
    }

    ADMIN_LIMITS = {
        COLLAGES_PER_DAYS: NO_LIMIT,
        EFFECTS: EXTENDED_EFFECTS,
        LOADINGS_PER_DAY: NO_LIMIT,
        NOTIFY_PERIOD: NO_LIMIT,
        PERMISSIONS: ADMIN_PERMISSIONS
    }

    USING_POLITICS_LIMITS = {
        UserType.DEFAULT: DEFAULT_LIMITS,
        UserType.SUBSCRIBER: SUBSCRIBER_LIMITS,
        UserType.BOT: DEFAULT_LIMITS,
        UserType.BANNED: BANNED_LIMITS,
        UserType.ADMIN: ADMIN_LIMITS
    }

    def __init__(self, user_type: UserType):
        """
        Инициализирует объект лимитов для указанного типа пользователя.

        Параметры:
            user_type (UserType): Тип пользователя.
        """
        super().__init__()
        self.value = UsingLimits.USING_POLITICS_LIMITS[user_type]

    def __str__(self):
        """
        Возвращает строковое представление объекта для удобного вывода.
        """
        return f"UsingLimits(value={self.value})"

    def __repr__(self):
        """
        Возвращает формальное строковое представление объекта.
        """
        return f"UsingLimits(value={self.value})"

    def to_dict(self):
        """
        Возвращает содержимое объекта в виде словаря.
        """
        return {
            "value": self.value
        }



if __name__ == "__main__":
    print("пример использования политик:")
    help(UsingLimits)
    print()

    for user_type in UserType:
        limits = UsingLimits(user_type)

        print(f"Лимиты для пользователя типа '{user_type.value}':")
        print(f"  Коллажей в день: {limits.value[COLLAGES_PER_DAYS]}")
        print(f"  Эффекты: {limits.value[EFFECTS]}")
        print(f"  Загрузка в день: {limits.value[LOADINGS_PER_DAY]}")
        print(f"  Период уведомления (дней): {limits.value[NOTIFY_PERIOD]}")
        print(f"  Разрешения: {limits.value[PERMISSIONS]}")
        print()
