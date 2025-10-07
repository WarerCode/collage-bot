"""
Здесь описан класс инкапсулирующий сообщение в телеграме.
Предоставляет интерфейс доступа к главным полям и мультимедия
"""

import telebot.types as types

import core.warerobjects.warerobject as warer
import core.dialog.media as media
import core.warerobjects.politics.content_policy as content_policy


class ContextMessage(warer.WarerObject):
    """

    """

    def __init__(self, message: types.Message):
        """

        """
        super().__init__()
        self.message = message

    @property
    def text(self):
        """

        """
        return self.message.text

    def __str__(self):
        """

        """
        return f"Message(message={self.message})"

    def __repr__(self):
        """

        """
        return f"(message={self.message})"

    def to_dict(self):
        """

        """
        return {
            "message" : self.message,
            "hints" : self.hints
        }

    def setup_media(self,
                    media: media.Media,
                    policy: content_policy.ContentPolicy):
        """

        """
        pass



if __name__ == "__main__":
    ...
