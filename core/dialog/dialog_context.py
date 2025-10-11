"""
Здесь представлена реализация класса, хранящего контекст
диалога пользователя с ботом:
Текущее сообщение, пользователь и положение в дереве диалога.
"""

import os
import telebot.types as types

import core.warerobjects.warerobject as warer
import core.dialog.message as contextMsg
import core.dialog.dialog_tree as dialog_tree
import core.user as user
import core.warerobjects.management.database as database
import core.warerobjects.politics.using_policy as using_policy
import core.warerobjects.data.userinfo as userinfo


class DialogContext(warer.WarerObject):
    """
    Класс, описывающий полное состояние диалога.

    Родители:
        warer.WarerObject
        abc.ABC
    """

    def __init__(self,
                 message: types.Message,
                 state: dialog_tree.DialogTree=dialog_tree.DialogTree.DIALOG_ROOT):
        """
        Инициализирует self.
        """
        super().__init__()
        self.user = user.User.from_message(message)
        self.message = contextMsg.ContextMessage(message)
        self.state = state  # по умолчанию - начало диалога

        db = database.Database(database.DBTypes.POSTGRESQL,
                      host=os.getenv("DB_HOST"),
                      database=os.getenv("DB_NAME"),
                      user=os.getenv("DB_USER"),
                      password=os.getenv("DB_PASSWORD"))
        self.__init_user(message.from_user.id, db)

    def __init_user(self, user_id: int, db: database.Database):
        """
        Функция используется один раз при инициализации
        контекста для проверки наличия информации о пользователе
        в базе данных. Инициализирует пользователя.
        """
        query, params = database.BaseQueries.select(
            database.TableNames.USERS,
            ["user_id", "username", "status"],
            conditions={"user_id": user_id}
        )
        user_info = db.fetch_one(query, params)

        if user_info:
            res_user = user.User(
                userinfo.UserInfo(user_info.get("user_id"), user_info.get("username")),
                using_policy.UsingPolicy(user_info.get("status"))
            )
            self.user = res_user

    def __str__(self):
        """
        Удобное строковое представление объекта.
        """
        return (f"<DialogContext: user_id={self.user.user_info.user_id}, "
                f"username={self.user.user_info.username}, "
                f"state={self.state}, "
                f"text={self.message.text}>")

    def __repr__(self):
        """
        Техническое строковое представление объекта.
        """
        return (f"DialogContext(user={repr(self.user)}, "
                f"message={repr(self.message)}, "
                f"state={self.state})")

    def to_dict(self):
        """
        Преобразует объект в словарь (например, для логирования или сериализации).
        """
        return {
            "user_id": self.user.user_info.user_id,
            "username": self.user.user_info.username,
            "state": str(self.state),
            "text": self.message.text
        }



if __name__ == "__main__":
    help(DialogContext)

    from telebot.types import Message, Chat, User
    import time

    # Минимальный мок-объект User (пустой бот-пользователь)
    mock_user = User(
        id=0,
        is_bot=True,
        first_name="Bot",
        username="demo_bot"
    )

    # Минимальный мок-объект чата
    mock_chat = Chat(
        id=0,
        type="private"
    )

    # Мок-сообщение
    mock_message = Message(
        message_id=1,
        from_user=mock_user,
        date=int(time.time()),
        chat=mock_chat,
        content_type="text",
        options={},
        json_string=None
    )
    mock_message.text = "Демонстрация"

    # ВАЖНО: отключаем загрузку из базы!
    # В DialogContext.__init__ временно закомментируй строку:
    # self.__init_user(...)

    # Создаём контекст
    context = DialogContext(message=mock_message)

    # Демонстрируем поля
    print("==== Демонстрация DialogContext ====")
    print("Тип объекта:", type(context))
    print("Поле .user:", context.user)
    print("Поле .message:", context.message)
    print("Поле .message.text:", context.message.text)
    print("Поле .state:", context.state)
