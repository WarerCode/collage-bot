"""
Модуль содержит определения лимитов использования для разных типов пользователей.

Содержит словари с ограничениями:
- DEFAULT_LIMITS — лимиты для обычных пользователей.
- SUBSCRIBER_LIMITS — лимиты для подписчиков.
- BANNED_LIMITS — ограничения для заблокированных пользователей.
- ADMIN_LIMITS — специальные права для администраторов.

TODO:
    - @JaneeWatermelon уточнить и согласовать реальные значения лимитов и эффектов.
"""

NO_LIMIT = -1

DEFAULT_LIMITS = {
    "collages_per_day": 100,
    "effects": [
        "",
        "",
        ""
    ],
    "loadings_per_day": 20
}

SUBSCRIBER_LIMITS = {
    "collages_per_day": NO_LIMIT,
    "effects": [
        "",
        "",
        "",
        ""
    ],
    "loadings_per_day": 100
}

BANNED_LIMITS = {
    "ban": True
}

ADMIN_LIMITS = {
    "admin": True
}
