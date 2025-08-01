import random
import re
import telebot
from telebot import types
from collections import defaultdict
import threading
import os
from dotenv import load_dotenv  # for parsing .env file


MAX_FILE_SIZE = 2 * 1024 * 1024 # 2 MB
EXPECTED_FORMATS = [".jpg", ".png", ".jpeg", ".webp"]
MAX_TAG_LENGTH = 30
MAX_INLINE_COLS = 3 # max count of columns in inline keyboard
MAX_INLINE_ROWS = 2 # max count of rows in inline keyboard

# once initialize keyboard as global scoped
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

MAKE_COLLAGE = "Составить коллаж"
LOAD_IMAGE = "Загрузить изображение"
START = "start"
COMMANDS = [MAKE_COLLAGE, LOAD_IMAGE, START]

get_collage_action = types.KeyboardButton(MAKE_COLLAGE)
load_image_action = types.KeyboardButton(LOAD_IMAGE)

markup.add(get_collage_action, load_image_action)

# Timer for bulk load images
album_timers = defaultdict(threading.Timer)
album_lock = threading.Lock()
AWAITING_FOR_LOAD_IMAGE = "Жду изображения для load_image"

load_dotenv('./config.env')
BOT_API_KEY = os.getenv('BOT_API_KEY')
MEDIA_ROOT = os.getenv('MEDIA_ROOT')


def restart_album_timer(media_group_id):
    """Перезапускает таймер для альбома"""
    # Останавливаем предыдущий таймер, если был
    if media_group_id in album_timers:
        album_timers[media_group_id].cancel()

    # Создаем новый таймер на 1 секунды
    timer = threading.Timer(1.0, process_bulk_images, args=[cached_messages[media_group_id]])
    album_timers[media_group_id] = timer
    timer.start()


STATES = {
    AWAITING_FOR_LOAD_IMAGE: False
}

cached_messages = defaultdict(list)

HELLO_MSG = r"""                 
<b><i>Да здравствует, ваше Величество!</i></b>                                                                                  

Я - рыцарь <b>CollageBot</b>, что был призван охранять фоторафии моих сузеренов и давать к ним отрытый доступ. 

 ⚔️ Вот поподробнее о моих функциях:

🗡 <code>\load_image</code> – с помощью электронных голубей, делаю ваши изображения достоянием для жителей всего королевства.

🗡 <code>\get_collage</code> – создаю коллаж по вашим запросам, ища материалы в великой библиотеке "База данных".
                     """

TAGS_PLS_MSG = r"""
<b><i>Ваше сиятельство, оно прекрасно!</i></b>

Теперь, пришла пора выбрать какие теги будут защитниками, чтобы ваше замечательное изображение не затерялось!

📖Вот инструкция по составлению тегов:

1. <b>Теги пишутся с символом</b> "<b>#</b>", чтобы не убежали👀 (Например: #красота).

2. <b>Если в одном теге хотите несколько слов, то смело вперёд</b>▶️ (Например: #гордостьипредубеждение)

3.  <b>Если хотите написать больше одного тега, то тогда пишите их через пробел</b>, я боюсь как им не было тесно👬 (Например: #гордостьипредубеждение #красота #достоинство)
"""

LOAD_IMAGE_MANUAL_MSG = rf"""
                <b><i>Ваше превосходительство, слушаюсь и повинуюсь!</i></b>

Выберите изображение, которое желаете отправить в сокровищницу.

👑Ограничения королевского декрета для файлов:                                                          

1. <b>Формат</b>: {", ".join(EXPECTED_FORMATS)} (в противном случае свитки сгниют📜)

2. <b>Цензура</b>: не 18+ контент (😭😭😭)

3. <b>Размер</b>: не более 2MB (иначе голуби не долетят🕊)
 
4. <b>Вид</b>: отправка файла в сжатом виде (не хочу марать ваши величественные длани🥰)
                """

UNEXPECTED_MSG = r"""
Ваше величество, ваши изречения слишком сложны для вашего покорного слуги, чтобы он что-то смог понять.😔
                            
<b>Пожалуйста, используйте кнопки.</b>
"""

SUCCESS_MSG = r"""✅<b>Всё прошло успешно, ваше величество!
Уверен вашему изображению сулит большая слава.</b>
"""

USER_MISTAKE_GETUP_MSGS = [
r"""❌<b>Ошибка.</b>

Ваше превосходительство, ошибается только тот, кто горит рвением, проверьте, следовали ли вы декрету.
""",

r"""❌<b>Ошибка.</b>

Мой король, настойчивость - мать удачи, попробуйте снова, следуя декрету.
""",

r"""❌<b>Ошибка.</b>

Ваше величество, Иерусалим не за 1 день захватили и не раз, не отчаивайтесь, декрет вам укажет путь.
""",

r"""❌<b>Ошибка.</b>

Ваше величество, я с вами до конца, не опускайте рук, декрет создан, чтобы не ошибаться.
"""
]

def user_mistake_msg() -> str:
    return random.choice(USER_MISTAKE_GETUP_MSGS)

def is_valid_tags(hashtags: list[str]) -> tuple[bool, list[str]]:
    errors = []
    res = True
    if not hashtags:
        errors.append("@topShizoid - empty tags list msg :: common.py")
        res = False

    for tag in hashtags:
        # if not tag.startswith('#'):
        #     errors.append(f"@topShizoid - invalid tag's {tag} start msg :: common.py")
        #     res = False

        if len(tag) > MAX_TAG_LENGTH:
            errors.append(f"@topShizoid - too large tag {tag} msg :: common.py")
            res = False

        # if not re.fullmatch(r'#\w+', tag):
        #     errors.append(f"@topShizoid - invalid tag's {tag} syntax msg :: common.py")
        #     res = False

    return (res, errors)