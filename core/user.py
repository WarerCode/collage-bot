"""
Здесь описывается общая структура пользователя бота.
"""

import typing
import telebot.types as types

import core.warerobjects.warerobject as warer
import core.warerobjects.politics.using_policy as using_policy
import core.warerobjects.politics.using_limits as using_limits
import core.warerobjects.data.userinfo as userinfo


class User(warer.WarerObject):
    """
    
    """
    
    def __init__(self,
                 info: userinfo.UserInfo,
                 policy: using_policy.UsingPolicy):
        """

        """
        super().__init__()
        self.info = info
        self.policy = policy

    @staticmethod
    def from_message(message: types.Message):
        """
        Возвращает дефолтного пользователя по сообщению.
        Не обращается к базе данных. Используется, когда
        пользователь встречается впервые.
        """
        return User(
            userinfo.UserInfo(
                message.from_user.id,
                message.from_user.username
            ),
            using_policy.UsingPolicy(
                using_limits.UserType.DEFAULT
                if not message.from_user.is_bot
                else using_limits.UserType.BOT
            )
        )

    def action(self, change_limits: typing.Callable):
        def wrapper(user: User):
            change_limits(user)
        return wrapper

    def __str__(self):
        """
        Удобное строковое представление пользователя.
        """
        return f"<User: id={self.info.user_id}, username={self.info.username}, policy={self.policy}>"

    def __repr__(self):
        """
        Формальное представление пользователя.
        """
        return f"User(info={self.info}, policy={self.policy})"

    def to_dict(self):
        """
        Представление пользователя в виде словаря.
        """
        return {
            "user_id": self.info.user_id,
            "username": self.info.username,
            "user_type": str(self.policy)
        }



if __name__ == "__main__":
    help(User)

    print("Пример объекта пользователя:")
    user: User = User(
        userinfo.UserInfo(
            0xF2132,
            "@DanilaGit"
        ),
        using_policy.UsingPolicy(
            using_limits.UserType.DEFAULT
        )
    )
    print(user)
