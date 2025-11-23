"""

"""

import telebot.types as types

import core.warerobjects.warerobject as warer
import core.user as user
import core.bot as collage_bot
import core.dialog.dialog_context as dialog_context
import core.warerobjects.management.pay_manager as business


class BotRouter(warer.WarerObject):
    """
    Класс-обертка для контроля над поведением бота. Инициализация происходит
    по текущему сообщению в новом чате.

    Родители:
        abc.ABC
        warer.WarerObject
    """

    def __init__(self, bot: collage_bot.CollageBot, message: types.Message):
        """
        Инициализирует self на основе нового сообщения.
        """
        super().__init__()
        self.bot = bot
        self.user = user.User.from_message(message)
        self.context = dialog_context.DialogContext(message)
        self.pay_manager = business.PayManager(message.from_user.id)

    def load_image(self, message: types.Message):
        """

        """
        self.bot.load_image(message)

    def make_collage(self, message: types.Message):
        """

        """
        self.bot.make_collage(message)



if __name__ == '__main__':
    pass
