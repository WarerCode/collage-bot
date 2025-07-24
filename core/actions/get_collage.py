import re
from telebot import types
from PIL import Image
from math import floor, sqrt
from common import MAX_INLINE_ROWS, MAX_INLINE_COLS
from database import *
from difflib import SequenceMatcher

load_dotenv('config.env')
MEDIA_ROOT = os.getenv('MEDIA_ROOT')

LOGO = open("core/assets/logo.jpg", 'rb')
CAPACITY_SEQUENCE = [2, 4, 9]
MAX_SHEET_SIZE = (1024, 1024)

def prompt_to_list(prompt: str):
    prompt = prompt.lower()
    hashtags = list(map(lambda x: x[1:], re.findall(r'#\w+', prompt)))
    prompt = re.sub(r'#\w+', '', prompt)
    prompt = re.sub(r'\W', '', prompt)
    words = prompt.split()

    return list(set(hashtags + words))

# Получение тегов с такими же первыми буквами (список названий)
def get_close_tags_by_prompt(prompt: str, threshold: float=0.6):
    maybe_tags = prompt_to_list(prompt)

    try:
        tags = []
        db_tags = get_start_tags(maybe_tags)

        for db_tag in db_tags:
            for maybe_tag in maybe_tags:
                acceptance = SequenceMatcher(a=db_tag, b=maybe_tag).ratio()
                if acceptance >= threshold:
                    tags.append(db_tag)
                    break

        return tags

    except Exception as e:
        print(f"Ошибка при получении похожих тегов: {e}")
        return []

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
        imgs = [Image.open(f"{MEDIA_ROOT}/images/"+id+".jpg") for id in file_ids]
        collage = imgs[0]

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