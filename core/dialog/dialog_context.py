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

    def __init_user(self, user_id: int) -> user.User:
        """
        Функция используется один раз при инициализации
        контекста для проверки наличия информации о пользователе
        в базе данных. Инициализирует пользователя.
        """
        with database.db.get_connection() as conn:
            pass



if __name__ == "__main__":
    help(DialogContext)
