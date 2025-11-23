"""

"""

import telebot
import os
import enum

import core.dialog.message as context_message
import core.dialog.dialog_context as context
import core.user as user


class Commands(enum.Enum):
    """

    """
    LOAD_IMAGE = "/load_image"
    MAKE_COLLAGE = "/make_collage"
    DELETE_MY_DATA = "/delete_my_data"


class CollageBot(telebot.TeleBot):
    """

    """

    def __init__(self, message: telebot.types.Message):
        """

        """
        super().__init__(os.getenv("BOT_API_KEY"))
        self.client = user.User.from_message(message)
        self.context = context.DialogContext(message)


    def on_answer(self, reply: context_message.ContextMessage):
        """

        """
        pass

    def load_image(self, request: telebot.types.Message):
        """

        """
        pass

    def make_collage(self, request: telebot.types.Message):
        """

        """
        pass

    def delete_my_data(self):
        """

        """
        pass

    def break_dialog(self):
        """

        """
        pass



if __name__ == "__main__":
    pass
