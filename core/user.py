"""
Здесь описывается общая структура пользователя бота.
Реализован CRUD-like интерфейс пользователя:
создание по информации из бд,
сохранение в бд.
см. подробнее в database.py
"""

import datetime
import time
import telebot.types as types

from core.warerobjects.management import database
import core.warerobjects.warerobject as warer
import core.warerobjects.politics.using_policy as using_policy
import core.warerobjects.politics.using_limits as using_limits
import core.warerobjects.data.userinfo as userinfo

UserType = using_limits.UserType

class User(warer.WarerObject):
    """
    Класс, наиболее полным образом описывающий пользователя бота.
    Хранит информацию как о пользователе Telegram, так и о предыдущих
    сессиях с ботом.

    Родители:
        warer.WarerObject
        abc.ABC
    """
    
    def __init__(self,
                 info: userinfo.UserInfo=userinfo.UserInfo(),
                 policy: using_policy.UsingPolicy=using_policy.UsingPolicy(UserType.DEFAULT)):
        """
        Инициализирует self.
        """
        super().__init__()
        self.info = info
        self.policy = policy

    @classmethod
    def from_message(cls, message: types.Message) -> 'User':
        """
        Возвращает дефолтного пользователя по сообщению.
        Не обращается к базе данных. Используется, когда
        пользователь встречается впервые.
        """
        tg_user = message.from_user
        user_fields = userinfo.UserFields

        user_type = UserType.BOT \
            if tg_user.is_bot \
            else UserType.DEFAULT
        args = {
            user_fields.USER_ID.value: tg_user.id,
            user_fields.USERNAME.value: tg_user.username,
            user_fields.IS_BOT.value: tg_user.is_bot,
            user_fields.STATUS.value: UserType.DEFAULT,
            user_fields.FIRST_NAME.value: tg_user.first_name,
            user_fields.LAST_NAME.value: tg_user.last_name,
            user_fields.LANGUAGE_CODE.value: tg_user.language_code,
            user_fields.IS_PREMIUM.value: tg_user.is_premium,
            user_fields.FREE_COLLAGES_REMAINING.value:
                using_limits.UsingLimits.USING_POLITICS_LIMITS[user_type].get(
                    using_limits.COLLAGES_PER_DAYS
                ),
            # будем считать, что сегодня новый пользователь создаст коллаж
            user_fields.LAST_COLLAGE_DATE.value: message.date,
            user_fields.UPDATED_AT.value: message.date,
            user_fields.CREATED_AT.value: message.date,
        }
        return User(
            userinfo.UserInfo(**args),
            using_policy.UsingPolicy(user_type)
        )
    
    @classmethod
    def from_db(cls, db_user: dict) -> 'User':
        """
        Возвращает дефолтного пользователя по сообщению.
        Не обращается к базе данных. Используется, когда
        пользователь встречается впервые.
        """
        user_fields = userinfo.UserFields

        user_type = UserType.BOT \
            if db_user.get(user_fields.IS_BOT.value) \
            else UserType.DEFAULT
        args = {}

        match = database.FieldsMatches.db_to_class(database.MatchesTypes.TG_USER)
        for key, val in db_user.items():
            class_key = match.get(key, key)
            if class_key is None:
                continue
            args[class_key] = val

        return User(
            userinfo.UserInfo(**args),
            using_policy.UsingPolicy(user_type)
        )

    def decrement_limits(self, limit: str, dec: int=1, reset: bool=False):
        """
        Метод для регулирования ограничений на пользование ботом.

        Параметры:
            reset: bool - может использоваться для бана, например
        """
        self.policy.limits[limit] -= abs(dec)
        if reset or self.policy.limits[limit] < 0:
            self.policy.limits[limit] = 0

    def update_limits(self, limit: str, reset: bool=False):
        """
        Обновляет конкретное ограничение (коллажи в день/загрузки)
        или полностью восстанавливает значение всех ограничений.

        Параметры:
            reset: bool - полностью восстанавливает лимиты, например, в
            начале следующего дня.
        """
        user_type = self.policy.usertype
        self.policy.limits[limit] = using_limits.UsingLimits.USING_POLITICS_LIMITS[user_type][limit]
        if reset:
            """Здесь полностью обновляются ограничения."""
            self.policy = using_limits.UsingLimits.USING_POLITICS_LIMITS[user_type]

    def change_status(self, new_status: UserType):
        """
        Заменяет статус пользователя и обновляет лимиты использования.
        """
        self.policy = using_policy.UsingPolicy(new_status)
        self.info.__setattr__(userinfo.UserFields.STATUS.value, new_status)

    def ban(self):
        """
        Метод для бана пользователя!!!
        """
        self.change_status(UserType.BANNED)

    def update_timestamp(self):
        """
        Метод обновления времени пользования бота.
        """
        self.info.update_timestamp()

    def save_to_db(self):
        """
        Применяется в конце диалога для сохранения/обновления
        информации о пользователе.
        """
        #TODO: @JaneeWatermelonka
        pass

    @classmethod
    def read_from_db(cls, id) -> 'User':
        """
        Метод для создания пользователя по его айдишнику.
        Информация о пользователе читается из базы.

        Параметры:
            id (PRIMARY_KEY~int): сигнатура не специфицирована,
            подразумевается первичный ключ отношения пользователей.
        """
        #TODO: @JaneeWatermelonka
        pass

    def __str__(self):
        """
        Удобное строковое представление пользователя.
        """
        return f"<User: userinfo={self.info}, policy={self.policy}>"

    def __repr__(self):
        """
        Формальное представление пользователя.
        """
        return f"User(info={self.info}, policy={self.policy})"

    def to_dict(self):
        """
        Представление пользователя в виде словаря.
        """
        return self.__dict__

class UserCache:
    def __init__(self):
        self._users = {}  # user_id -> User
    
    def need_sync(self, user_id: int, ttl: int = 300) -> bool:
        now = datetime.datetime.now()
        user = self._users.get(user_id)

        if user is None:
            return True

        last = user.info.to_dict().get(userinfo.UserFields.UPDATED_AT.value)

        if last is None:
            return True

        return now - last > datetime.timedelta(seconds=ttl)
    
    @property
    def users(self):
        return self._users
    
    def update_user(self, id: int, user: User):
        self._users[id] = user


if __name__ == "__main__":
    help(User)

    print("Пример объекта пользователя:")
    user: User = User(
        userinfo.UserInfo(
            user_id=0xF2132,
            username="@DanilaGit",
            first_name="Danila",
            last_name="Efimov",
            is_bot=False,
            is_premium=True
        ),
        using_policy.UsingPolicy(
            UserType.DEFAULT
        )
    ).info
    print(user)
