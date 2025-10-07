"""

"""

import telebot.types as types

import core.warerobjects.warerobject as warer


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
            "message" : self.message
        }



if __name__ == "__main__":
    ...
