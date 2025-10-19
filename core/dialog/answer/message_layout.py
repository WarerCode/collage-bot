"""
Здесь описан класс сборщика ответа от бота.
Реализован интерфейс
"""

import telebot.types as types

import core.warerobjects.warerobject as warer
import core.dialog.message as message_context
import core.warerobjects.politics.content_policy as content_policy


class ReplyBuilder(warer.WarerObject):
    """

    """

    @classmethod
    def build_reply(cls,
                    message: message_context.ContextMessage,
                    policy: content_policy.ContentPolicy) -> types.Message:
        """
        Контекст сообщения хранит медиа и последнее сообщение от пользователя.
        Политика контента определяет вид сообщения от бота:
        позиционирование, медиа и т.п.
        """
        image_paths = policy[content_policy.Hints.IMAGE_PATHS]
        pass

    @staticmethod
    def apply_triggers(message: types.Message,
                       policy: content_policy.ContentPolicy):
        """

        """
        for trigger in content_policy.TRIGGERS:
            message.



if __name__ == "__main__":
    pass
