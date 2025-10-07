"""

"""

import telebot.types as types

import core.warerobjects.warerobject as warer
import core.dialog.message as contextMsg


class DialogContext(warer.WarerObject):
    """

    """

    def __init__(self, message: types.Message):
        """

        """
        super().__init__()
        self.message = contextMsg.ContextMessage(message)



if __name__ == "__main__":
    ...
