"""
Здесь описан класс сборщика ответа от бота.
Реализован интерфейс для построения медиа-объектов и формирования
итогового ответа пользователю на основе политики контента.
"""

import telebot.types as types

import core.warerobjects.content_types.image
import core.warerobjects.warerobject as warer
import core.dialog.message as context_message
import core.warerobjects.politics.content_policy as content_policy
import core.dialog.media as media
import core.warerobjects.content_types.base_type as base_type
import core.warerobjects.content_types.text as text
import core.warerobjects.content_types as content_types
import core.exceptions as exceptions
from core.warerobjects.data.metadata import MetaData


class MediaFabric(warer.WarerObject):
    """
    Класс-фабрика для создания медиа-объектов по пути к файлу.

    Предоставляет метод для определения типа медиа-данных (изображение, видео и т.п.)
    на основе расширения файла и создания соответствующего объекта контент-типа.
    """

    TYPE_MAP = {
        "png": content_types.image.Image,
        "jpg": content_types.image.Image
        # other content extensions ...
    }

    @staticmethod
    def build(path: str) -> base_type.BaseMediaType:
        """
        Создает объект медиа-данных по пути к файлу.

        Определяет тип контента по расширению и создает экземпляр
        соответствующего класса из TYPE_MAP.

        Параметры:
            path (str): Путь к файлу медиа-объекта (например, '/images/cat.png').

        Возвращает:
            BaseMediaType: Экземпляр медиа-класса, соответствующий типу файла.

        Исключения:
            ContentError: Если расширение файла не поддерживается.
        """
        extension = path.split('.')[-1]
        media_type = MediaFabric.TYPE_MAP.get(extension)

        if not media_type:
            raise exceptions.ContentError(f"core.dialog.answer.MediaFabric: unsupported media file extension [{extension}]")

        return media_type(path)


class ReplyBuilder(warer.WarerObject):
    """
    Класс, реализующий методы для сборки ответа пользователю.

    Используется для подготовки текста, медиа-данных и форматирования ответа
    в соответствии с политикой контента (ContentPolicy) и контекстом диалога.
    """

    @staticmethod
    def get_media(policy: content_policy.ContentPolicy) -> media.Media:
        """
        Формирует объект Media на основе данных политики контента.

        Извлекает пути к файлам медиа (например, изображений) из политики
        и создает список объектов контента с помощью MediaFabric.

        Параметры:
            policy (content_policy.ContentPolicy): Политика сборки сообщения.

        Возвращает:
            media.Media: Объект, содержащий список медиа-контента для отправки.
        """
        media_paths = policy[content_policy.Hints.MEDIA_PATHS]
        content = [MediaFabric.build(path) for path in media_paths]
        return media.Media(content)

    @staticmethod
    def get_text(policy: content_policy.ContentPolicy) -> text.Text:
        """
        Создает объект текста на основе данных из политики контента.

        Извлекает исходный текст из поля политики и оборачивает его
        в объект text.Text для дальнейшего использования при сборке сообщения.

        Параметры:
            policy (content_policy.ContentPolicy): Политика сборки сообщения.

        Возвращает:
            text.Text: Текстовый объект, готовый к вставке в ответ.
        """
        raw_text = policy[content_policy.Hints.RAW_TEXT]
        return text.Text(raw_text if raw_text else "")

    @staticmethod
    def apply_text_format(media_data: media.Media,
                          policy: content_policy.ContentPolicy):
        """
        Применяет форматирование к текстовому содержимому медиа-данных.

        Извлекает тип форматирования из политики (например, HTML, Markdown)
        и устанавливает соответствующую подсказку (hint) для объекта Media.

        Параметры:
            media_data (media.Media): Объект, содержащий медиа-контент.
            policy (content_policy.ContentPolicy): Политика сборки сообщения.
        """
        format_type = content_policy.Hints.CAPTION_FORMAT
        media_data.set_hint(format_type, policy[format_type])

    @staticmethod
    def get_reply_message(message: types.Message,
                          media_data: media.Media) -> context_message.ContextMessage:
        """
        Формирует итоговый объект ответа пользователю.

        На основе входящего сообщения и подготовленных медиа-данных
        создается объект ContextMessage, готовый к отправке через Telegram API.

        Параметры:
            message (types.Message): Исходное сообщение пользователя.
            media_data (media.Media): Подготовленные данные для ответа.

        Возвращает:
            context_message.ContextMessage: Объект, содержащий ответ с контентом.
        """
        return context_message.ContextMessage(message, media_data)



if __name__ == "__main__":
    # demo.py
    from core.warerobjects.politics import content_policy
    from core.warerobjects.content_types import text
    from telebot.types import Message, User, Chat

    # === Подготовка политики контента ===
    policy_data = {
        content_policy.Hints.MEDIA_PATHS: [r"./core/assets/test/1_1.jpg"],
        content_policy.Hints.RAW_TEXT: "Привет! Смотри на этих милых животных 🐱🐶",
        content_policy.Hints.CAPTION_FORMAT: "Markdown"
    }
    policy = content_policy.ContentPolicy(MetaData.from_dict(policy_data))

    # === Создаем медиа ===
    media_data = ReplyBuilder.get_media(policy)
    print("Собранные медиа:")
    for item in media_data.content:
        print(f" - {item}")

    # === Создаем текст ===
    text_data = ReplyBuilder.get_text(policy)
    print("\nТекст для ответа:")
    print(text_data)

    # === Применяем форматирование текста к медиа ===
    ReplyBuilder.apply_text_format(media_data, policy)
    print("\nПримененные подсказки к медиа:")
    print(media_data.hints)

    # === Создаем объект сообщения для ответа ===
    user = User(id=0, is_bot=False, first_name="Danila")
    chat = Chat(id=1, type="private")
    fake_message = Message(message_id=1,
                           from_user=user,
                           chat=chat,
                           date=1234567890,
                           content_type=None,
                           options={},
                           json_string=None)
    reply_message = ReplyBuilder.get_reply_message(fake_message, media_data)

    print("\nСформированный объект сообщения:")
    print(reply_message)
