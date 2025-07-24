import telebot
from telebot import types
import social_collage
from PIL import Image
from math import floor, sqrt
from core.common import MAX_INLINE_ROWS, MAX_INLINE_COLS
from core.database import get_images_by_tags

LOGO = open(r"E:\портфолио студента\материалы\2024 - 2025\events\summer\collage bot\core\assets\logo.jfif", 'rb')
CAPACITY_SEQUENCE = [2, 4, 9]
MAX_SHEET_SIZE = (1024, 1024)

def get_collage_by_tags(hashtags: list[str]):
    """
    The core of get collage feature
    here building a collage by Pillow
    :param hashtags: list of tags from user
    :return: status (ok), error messages (errors) and collage (IOBynary)
    """
    # return values
    ok = True
    errors = []

    file_ids = get_images_by_tags(hashtags)



    # calculate count of photos - DONE
    count = photo_count(len(file_ids))
    file_ids = file_ids[0:count]

    # calculate grid
    # calculate basic size of field
    # randomly increment size
    # build grid layout

    if not file_ids:
        errors.append("@topShizoid - failed to get file ids for collage msg :: common.py")
        ok = False

    try:
        imgs = [Image.open(r"E:/портфолио студента/материалы/2024 - 2025/events/summer/collage bot/core/images/"+id+".jpg") for id in file_ids]
        collage = social_collage.collage_4_2(
        imgs,
        bgcolor=(255, 255, 255),
        spaceshare=0,
        )

    except Exception as e:
        errors.append(f"get_collage.get_collage_by_tags::troubles : {e}")
        ok = False
        collage = LOGO

    return ok, errors, collage


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


def photo_count(size: int):
    res = size
    for c in CAPACITY_SEQUENCE:
        if size < c:
            return res
        res = c
    return CAPACITY_SEQUENCE[-1]


def field_size(count: int, sheet_size: (int, int)):
    photo_in_row = floor(sqrt(count))