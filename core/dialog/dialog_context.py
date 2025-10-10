"""
Здесь представлена реализация класса, хранящего контекст
диалога пользователя с ботом:
Текущее сообщение, пользователь и положение в дереве диалога.
"""

import telebot.types as types

import core.warerobjects.warerobject as warer
import core.dialog.message as contextMsg
import core.dialog.dialog_tree as dialog_tree
import core.user as user
import core.warerobjects.management.database as database
import core.warerobjects.politics.using_policy as using_policy
import core.warerobjects.data.userinfo as userinfo
import core.warerobjects.politics.using_limits as using_limits


class DialogContext(warer.WarerObject):
    """
    Класс, описывающий полное состояние диалога.

    Родители:
        warer.WarerObject
        abc.ABC
    """

    def __init__(self,
                 message: types.Message,
                 state: dialog_tree.DialogTree=dialog_tree.DialogTree.DIALOG_TREE):
        """
        Инициализирует self.
        """
        super().__init__()
        self.user = user
        self.message = contextMsg.ContextMessage(message)
        self.state = state  # по умолчанию - начало диалога

    def __init_user(self, user_id: int, db: database.Database) -> user.User:
        """
        Функция используется один раз при инициализации
        контекста для проверки наличия информации о пользователе
        в базе данных. Инициализирует пользователя.
        """
        query, params = database.BaseQueries.select(database.TableNames.USERS, ["user_id", "username", "status"], conditions={"user_id": user_id})
        user_info = db.fetch_one(query, params)

        if user_info:
            res_user = user.User(
                userinfo.UserInfo(user_info.get("user_id"), user_info.get("username")),
                using_policy.UsingPolicy(user_info.get("status"))
            )
        else:
            res_user = None

        return res_user



if __name__ == "__main__":
    help(DialogContext)
