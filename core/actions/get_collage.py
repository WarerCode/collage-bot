import random
from io import BytesIO
import re
from telebot import types
from PIL import Image
from math import floor, sqrt
from common import MAX_INLINE_ROWS, MAX_INLINE_COLS
from database import *
from difflib import SequenceMatcher
from logs.logger import logger


class Direction:
    HORIZONTAL  = "horizontal"
    VERTICAL    = "vertical"


class Shape:
    SQUARE  = ((800, 800),  Direction.HORIZONTAL)
    WIDE    = ((1000, 500), Direction.HORIZONTAL)
    TALL    = ((500, 1000), Direction.VERTICAL)
    PHONE   = ((900, 1600), Direction.VERTICAL)
    PC      = ((1600, 900), Direction.HORIZONTAL)


load_dotenv('./config.env')
MEDIA_ROOT = os.getenv('MEDIA_ROOT')


LOGO = open("./core/assets/logo.jpg", 'rb')
CAPACITY_SEQUENCE = [2, 4, 9]
MAX_SHEET_SIZE = (1024, 1024)
ADD_SCALE = 1.1


def prompt_to_list(prompt: str):
    prompt = prompt.lower()
    hashtags = list(map(lambda x: x[1:], re.findall(r'#\w+', prompt)))
    prompt = re.sub(r'#\w+', '', prompt)
    prompt = re.sub(r'\W', ' ', prompt)
    words = list(word for word in prompt.split() if word)

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
        logger.error(f"Ошибка при получении похожих тегов: {e}")
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

    file_ids = get_images_by_tags(hashtags)[:9]
    random.shuffle(file_ids)

    # calculate grid
    # calculate basic size of field
    # randomly increment size
    # build grid layout

    if not file_ids:
        errors.append("@topShizoid - failed to get file ids for collage msg :: common.py")
        ok = False

    try:
        img_paths = [f"{MEDIA_ROOT}/images/"+id+".jpg" for id in file_ids][:9]
        collage = create_collage(img_paths)

    except Exception as e:
        errors.append(f"get_collage.get_collage_by_tags::troubles : {e}")
        ok = False
        collage = LOGO

    return ok, errors, collage


def get_rows_cols(n: int, direction: str=Direction.HORIZONTAL):
    def get_sides(n: int):
        k = int(n**0.5)

        while n / k != int(n / k) and k > 1:
            k -= 1

        if k == 1:
            new_n = int(n**0.5)**2
            if new_n != 1:
                return get_sides(new_n)
            else:
                return (k, n)
        else:
            return (k, n // k)
        
    low, high = get_sides(n)

    if direction == Direction.HORIZONTAL:
        return (low, high)
    else:
        return (high, low)


def resize_crop_to_fill(img, target_size, add_scale_frequency: float=0.5):
    """Масштабирует для заполнения всей ячейки"""
    target_ratio = target_size[0] / target_size[1]
    img_ratio = img.width / img.height

    k = ADD_SCALE if random.random() < add_scale_frequency else 1
    
    if target_ratio > img_ratio:
        img.thumbnail((target_size[0]*k, target_size[0]*3))
    else:
        img.thumbnail((target_size[1]*3, target_size[1]*k))
    
    return img


def create_collage(image_paths: list, shape_info: tuple=Shape.PHONE):
    """
    Создает коллаж из списка изображений
    """
    if not image_paths:
        raise ValueError("Нужен хотя бы один файл изображения")
    elif len(image_paths) == 1:
        return Image.open(image_paths[0])
    
    # Открываем все изображения
    images = [Image.open(img_path) for img_path in image_paths]
    
    output_size = shape_info[0]

    # Рассчитываем размеры сетки
    rows, cols = get_rows_cols(len(images), shape_info[1])
    cell_width = output_size[0] // cols
    cell_height = output_size[1] // rows
    
    # Создаем пустое изображение для коллажа
    collage = Image.new('RGB', output_size)

    enum_images = list(enumerate(images))
    random.shuffle(enum_images)

    # Вставляем изображения в сетку
    for i, img in enum_images:
        # Масштабируем изображение, сохраняя пропорции
        # img.thumbnail((cell_width, cell_height))
        img = resize_crop_to_fill(img, (cell_width, cell_height))
        
        # Вычисляем позицию
        x = (i % cols) * cell_width
        y = (i // cols) * cell_height
        
        # Вставляем изображение
        collage.paste(img, (x, y))
    
    # Сохраняем в BytesIO
    output = BytesIO()
    collage.save(output, format='JPEG')
    output.seek(0)
    
    # Закрываем все изображения
    for img in images:
        img.close()
    
    return output


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