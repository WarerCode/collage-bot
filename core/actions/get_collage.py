import telebot
from telebot import types
from core.common import MAX_INLINE_ROWS, MAX_INLINE_COLS


def get_collage_by_tags(hashtags: list[str]):
    return True, [], open(r"C:\Users\home\Pictures\sd_ultra_A_valiant_Right_Knight__c_2931246757.png", 'rb')


def build_inline_keyboard(hashtags: list[str]):
    board = []
    for i in range(MAX_INLINE_ROWS):
        line = []
        for j in range(MAX_INLINE_COLS):
            index = i * MAX_INLINE_COLS + j
            if index >= len(hashtags):
                break

            tag = hashtags[index]
            button = types.InlineKeyboardButton(tag, callback_data=tag)
            line.append(button)
        board.append(line)

    return types.InlineKeyboardMarkup(board)
