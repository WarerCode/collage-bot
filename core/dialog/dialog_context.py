"""

"""

import telebot.types as types

import core.warerobjects.warerobject as warer
import core.dialog.message as contextMsg
import core.dialog.dialog_tree as dialog_tree
import core.user as user


class DialogContext(warer.WarerObject):
    """

    """

    def __init__(self,
                 user: user.User,
                 message: types.Message,
                 state: dialog_tree.DialogTree=dialog_tree.DialogTree.DIALOG_TREE):
        """

        """
        super().__init__()
        self.user = user
        self.message = contextMsg.ContextMessage(message)
        self.state = state  # по умолчанию - начало диалога



if __name__ == "__main__":
    help(DialogContext)
