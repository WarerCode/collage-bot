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
from core.warerobjects.politics.size_policy import SizePolicy


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
    NO_PROMOTIONS = "no_promotions" # Без рекламы
    SEND_IMAGES = "send_images" # Отправка изображений
    CREATE_COLLAGE = "create_collage" # Создание коллажа
    EDIT_COLLAGE = "edit_collage" # Редактирование коллажа
    MORE_EFFECTS = "more_effects" # 

    # для супер пользователей
    UNLIMITED = "unlimited" # Все разрешения
    MANAGE_USERS = "manage_users" # Управление пользователями
    ACCESS_STATS = "access_stats" # Доступ к статистике
    CREATE_POLL = "create_poll" # Создание опросов

# Значение бесконечности для числовых атрибутов политики
NO_LIMIT = None


# Атрибуты политики использования
COLLAGES_PER_DAYS = "collages_per_day"
EFFECTS = "effects"
SISES = "sises"
LOADINGS_PER_DAY = "loadings_per_day"
NOTIFY_PERIOD = "notify_period"
PERMISSIONS = "permissions"

# Дефолтные значения эффектов и разрешений
DEFAULT_EFFECTS = ["default", "gray_scale", "blur", "noise"]
EXTENDED_EFFECTS = ["vignette", "frame", "stickers", "core"]
DEFAULT_SISES = [SizePolicy.Size.SQUARE, SizePolicy.Size.HORIZONTAL, SizePolicy.Size.VERTICAL]
EXTENDED_SISES = [SizePolicy.Size.HOR_PHONE, SizePolicy.Size.VER_PHONE]
DEFAULT_PERMISSIONS = [Permission.SEND_IMAGES, Permission.CREATE_COLLAGE, Permission.EDIT_COLLAGE]
SUBSCRIBE_PERMISSIONS = DEFAULT_PERMISSIONS + [Permission.NO_PROMOTIONS, Permission.MORE_EFFECTS]
ADMIN_PERMISSIONS = [Permission.UNLIMITED]
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
        SISES: DEFAULT_SISES,
        LOADINGS_PER_DAY: 20,
        NOTIFY_PERIOD: 3,
        PERMISSIONS: DEFAULT_PERMISSIONS
    }

    SUBSCRIBER_LIMITS = {
        COLLAGES_PER_DAYS: NO_LIMIT,
        EFFECTS: DEFAULT_EFFECTS + EXTENDED_EFFECTS,
        SISES: DEFAULT_SISES + EXTENDED_SISES,
        LOADINGS_PER_DAY: 100,
        NOTIFY_PERIOD: 7,
        PERMISSIONS: SUBSCRIBE_PERMISSIONS
    }

    BANNED_LIMITS = {
        COLLAGES_PER_DAYS: 0,
        EFFECTS: [],
        SISES: [],
        LOADINGS_PER_DAY: 0,
        NOTIFY_PERIOD: 2,
        PERMISSIONS: BANNED_PERMISSIONS
    }

    ADMIN_LIMITS = {
        COLLAGES_PER_DAYS: NO_LIMIT,
        EFFECTS: DEFAULT_EFFECTS + EXTENDED_EFFECTS,
        SISES: DEFAULT_SISES + EXTENDED_SISES,
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
        print(f"  Размеры: {limits.value[SISES]}")
        print(f"  Загрузка в день: {limits.value[LOADINGS_PER_DAY]}")
        print(f"  Период уведомления (дней): {limits.value[NOTIFY_PERIOD]}")
        print(f"  Разрешения: {limits.value[PERMISSIONS]}")
        print()
