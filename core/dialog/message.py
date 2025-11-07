"""
Здесь описан класс инкапсулирующий сообщение в телеграме.
Предоставляет интерфейс доступа к главным полям и мультимедия
"""

import enum
import telebot.types as types

import core.warerobjects.warerobject as warer
import core.dialog.media as media
import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.content_types.text as text


class MessageFields(enum.Enum):
    """
    Enum с основными полями объекта сообщения Telegram (telebot.types.Message),
    которые часто используются при обработке сообщений в боте.
    """
    MESSAGE_ID = 'message_id'
    FROM_USER = 'from_user'
    CHAT = 'chat'
    DATE = 'date'
    TEXT = 'text'
    CAPTION = 'caption'  # Подпись к медиа
    PHOTO = 'photo'
    VIDEO = 'video'
    AUDIO = 'audio'
    DOCUMENT = 'document'


class ContextMessage(warer.WarerObject):
    """
    Класс контекста, необходимого для сборки ответа юзеру.
    Хранит сообщение от пользователя и необходимый медиа контент.

    Родители:
        warer.WarerObject
        abc.ABC

    Атрибут экземпляра:
        reply_to_message (types.Message) - последнее сообщение от пользователя.
        content (list[media.Media]) - необходимые медиа для сборки ответа.
    """

    def __init__(self,
                 message: types.Message,
                 media_data: media.Media=None):
        """
        Инициализирует self.
        """
        super().__init__()
        self.reply_to_message = message
        self.media_data = media.Media([]) if not media_data else media_data

    @property
    def user_text(self):
        """
        Текст сообщения пользователя.
        """
        return self.reply_to_message.text

    def __str__(self):
        """
        Человекочитаемое представление объекта.
        """
        return f"ContextMessage(reply_to_message={self.reply_to_message}, media_data={self.media_data})"

    def __repr__(self):
        """
        Строковое представление для отладки.
        """
        return f"(reply_to_message={self.reply_to_message})"

    def to_dict(self):
        """
        Сериализация объекта в словарь.
        """
        return {
            "reply_to_message": self.reply_to_message,
            "hints": self.hints
        }



if __name__ == "__main__":
    from telebot.types import Message, User, Chat

    # Создаем имитацию объекта User
    fake_user = User(id=12345,
                     is_bot=False,
                     first_name="Иван",
                     last_name="Иванов",
                     username="ivan_ivanov")

    # Создаем имитацию объекта Chat
    fake_chat = Chat(id=67890, type="private")

    # Создаем имитацию объекта Message
    fake_message = Message(message_id=1,
                           from_user=fake_user,
                           chat=fake_chat,
                           date=1234567890,
                           content_type=None,
                           options={},
                           json_string=None)
    fake_message.text = "Hello, World!"

    # Создаем объект ContextMessage
    context = ContextMessage(message=fake_message)

    # Выводим текст из сообщения
    print("Текст пользователя:", context.user_text)

    # Выводим словарь представления
    print("Словарь объекта:", context.to_dict())
