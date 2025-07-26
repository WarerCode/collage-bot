import os
import threading
from dotenv import load_dotenv  # for parsing .env file
import telebot
from telebot import types
from actions.load_image import check_load_image_rules, extract_hashtags, load_image_save_to_database
from actions.get_collage import get_close_tags_by_prompt, get_collage_by_tags, build_inline_keyboard
from common import *        # bot
from database import *      # init popular tags
from collections import defaultdict
from logs.logger import logger

load_dotenv('./config.env')
BOT_API_KEY = os.getenv('BOT_API_KEY')
MEDIA_ROOT = os.getenv('MEDIA_ROOT')

bot = telebot.TeleBot(BOT_API_KEY)  # generates bot entity

# once initialize keyboard as global scoped
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

MAKE_COLLAGE = "Составить коллаж"
LOAD_IMAGE = "Загрузить изображение"
START = "start"
COMMANDS = [MAKE_COLLAGE, LOAD_IMAGE, START]

# Timer for bulk load images
album_timers = defaultdict(threading.Timer)
album_lock = threading.Lock()
AWAITING_FOR_LOAD_IMAGE = "Жду изображения для load_image"


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

get_collage_action = types.KeyboardButton(MAKE_COLLAGE)
load_image_action = types.KeyboardButton(LOAD_IMAGE)

markup.add(get_collage_action, load_image_action)
# TODO: optionally we can add info_action, which send links to us repo and all that ...

# initialize DB once (IF NOT EXIST)
init_db()

POPULAR_TAGS = get_most_popular_tags(4)
choose_board = build_inline_keyboard(POPULAR_TAGS)


logger.info("bot initialize finished")


@bot.message_handler(commands=[START])
def welcome(message) -> None:
    """
    Here we can use stickers and all that ...
    and action buttons like:
    info = types.KeyboardButton('About Us')
    :param message: telebot.types.Message
    :return: None
    """
    bot.send_message(message.chat.id,
                     HELLO_MSG, # common.py::
                     reply_markup=markup,
                     parse_mode='html')


@bot.message_handler(func=lambda m: m.text not in COMMANDS)
def non_request_text_handler(message):
    bot.send_message(message.chat.id,
                     UNEXPECTED_MSG,  # common.py::
                     reply_markup=markup,
                     parse_mode='html')


@bot.message_handler(content_types=['photo'])
def non_request_photo_handler(message):
    if STATES[AWAITING_FOR_LOAD_IMAGE]:
        try:
            if message.content_type != 'photo':
                raise ValueError("@topShizoid invalid content type msg :: common.py")

            os.makedirs(f'{MEDIA_ROOT}/images', exist_ok=True)

            if message.media_group_id:
                with album_lock:
                    restart_album_timer(message.media_group_id)
                    cached_messages[message.media_group_id].append(message)
            else:
                process_single_image(message)

            logger.info(f"bot.callback_load_image::success from user {message.chat.id}")

        except Exception as e:
            logger.error(f"bot.callback_load_image:: request text: {message.text}; chat: {message.chat.id}; Error: {e}")
            bot.reply_to(message, f"{e}\n",
                        parse_mode='html')
            bot.send_message(message.chat.id,
                            user_mistake_msg(),
                            parse_mode='html')
            bot.clear_step_handler(message)  # unregister next handler, clear context
    else:
        bot.send_message(message.chat.id,
                     UNEXPECTED_MSG,  # common.py::
                     reply_markup=markup,
                     parse_mode='html')


@bot.message_handler(content_types=['document'])
def file_handler(message):
    bot.send_message(message.chat.id,
                     user_mistake_msg(),  # common.py::
                     reply_markup=markup,
                     parse_mode='html')


@bot.message_handler(func=lambda m: m.text == LOAD_IMAGE)
def request_load_image(message):
    bot.send_message(
        message.chat.id,
        LOAD_IMAGE_MANUAL_MSG,
        parse_mode='html'
    )

    STATES[AWAITING_FOR_LOAD_IMAGE] = True


def process_bulk_images(messages):
    STATES[AWAITING_FOR_LOAD_IMAGE] = False
    file_ids = []
    for message in messages:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = bot.get_file(file_id)

        ok, errors = check_load_image_rules(file_info)
        if not ok:
            raise RuntimeError("\n\n".join(errors))

        downloaded_file = bot.download_file(file_info.file_path)

        file_path = f"{MEDIA_ROOT}/images/{file_id}.jpg"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        file_ids.append(file_id)

    del cached_messages[message.media_group_id]

    bot.reply_to(message, TAGS_PLS_MSG, parse_mode='html')
    bot.register_next_step_handler(
        message, 
        callback_load_image_tags, 
        kwargs={
            "user_id": message.from_user.id,
            "file_ids": file_ids,
            "media_group_id": message.media_group_id
        }
    )


def process_single_image(message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file_info = bot.get_file(file_id)

    ok, errors = check_load_image_rules(file_info)
    if not ok:
        raise RuntimeError("\n\n".join(errors))

    downloaded_file = bot.download_file(file_info.file_path)

    file_path = f"{MEDIA_ROOT}/images/{file_id}.jpg"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, TAGS_PLS_MSG, parse_mode='html')
    bot.register_next_step_handler(
        message, 
        callback_load_image_tags, 
        kwargs={
            "user_id": message.from_user.id,
            "file_id": file_id
        }
    )


def callback_load_image_tags(message, kwargs):
    """
    Tags are parsed and checked here,
    and then the buffered data is associated with the image and it's tags
    :param message: text from user
    :return: None
    """
    try:
        if message.content_type != 'text':
            raise ValueError("@topShizoid - invalid content type msg :: common.py")

        prompt = message.text
        hashtags = extract_hashtags(prompt)
        ok, errors = is_valid_tags(hashtags)

        if not ok:
            raise RuntimeError("\n\n".join(errors))
        
        user_id = kwargs.get("user_id")
        media_group_id = kwargs.get("media_group_id")

        if not media_group_id is None:
            # album message branch
            file_ids = kwargs.get("file_ids")
            ok = bulk_save_to_database(user_id, file_ids, media_group_id, hashtags)
        else:
            file_id = kwargs.get("file_id")
            ok, errors = load_image_save_to_database(user_id, file_id, hashtags)

        if not ok:
            raise RuntimeError("\n\n".join(errors))

        bot.reply_to(message, SUCCESS_MSG, parse_mode='html')

    except Exception as e:
        logger.error(f"bot.callback_load_image_tags:: request text: {message.text}; chat: {message.chat.id}; Error: {e}")
        bot.reply_to(message, f"{e}\n",
                     parse_mode='html')
        bot.send_message(message.chat.id,
                         user_mistake_msg(),
                         parse_mode='html')
        bot.clear_step_handler(message)  # unregister next handler, clear context


@bot.message_handler(func=lambda m: m.text == MAKE_COLLAGE)
def request_make_collage(message):
    global POPULAR_TAGS, choose_board
    POPULAR_TAGS = get_most_popular_tags(4)
    choose_board = build_inline_keyboard(POPULAR_TAGS)

    bot.send_message(
        message.chat.id,
        TAGS_PLS_MSG,
        parse_mode='html',
        reply_markup=choose_board
    )

    bot.register_next_step_handler(message, callback_make_collage)


def callback_make_collage(message):
    """
    Tags are parsed and verified here, and then
    a collage creation is attempted using the obtained tags
    :param message: text from user
    :return: None
    """
    try:
        if message.content_type != 'text':
            raise ValueError("@topShizoid - invalid content type msg :: common.py")

        prompt = message.text
        hashtags = get_close_tags_by_prompt(prompt)
        ok, errors = is_valid_tags(hashtags)

        if not ok:
            raise RuntimeError("\n\n".join(errors))

        ok, errors, collage = get_collage_by_tags(hashtags)

        if not ok:
            raise RuntimeError("\n\n".join(errors))

        increment_tag_popularity(hashtags)
        bot.send_photo(message.chat.id, collage)

    except Exception as e:
        logger.error(f"bot.callback_make_collage:: request text: {message.text}; chat: {message.chat.id}; Error: {e}")
        bot.reply_to(message, f"{e}\n",
                     parse_mode='html')
        bot.send_message(message.chat.id,
                         user_mistake_msg(),
                         parse_mode='html')
        bot.clear_step_handler(message)  # unregister next handler, clear context


@bot.callback_query_handler(func=lambda call: call.data in POPULAR_TAGS)
def inline_buttons_handler(call):
    """
    This is just a wrapper encapsulating
    the call to the make_collage handler
    :param message: text from user
    :return: None
    """
    try:
        # answer the callback to stop the loading spin
        bot.answer_callback_query(call.id)

        hashtags = [call.data]
        ok, errors, collage = get_collage_by_tags(hashtags)
        if not ok:
            raise RuntimeError("\n\n".join(errors))

        bot.send_photo(call.message.chat.id, collage)

    except Exception as e:
        logger.error(f"bot.inline_buttons_handler:: chat: {call.message.chat.id}; Error: {e}")
        bot.reply_to(call.message, f"{e}\n",
                     parse_mode='html')
        bot.send_message(call.message.chat.id,
                         user_mistake_msg(),
                         parse_mode='html')

    bot.clear_step_handler(call.message) # unregister next handler, clear context


# vvv RUNNING vvv
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except ConnectionError as e:
        logger.error('Network error: ', e)
    except Exception as r:
        logger.error("Unexpected error: ", r)
    finally:
        logger.info("running finished")