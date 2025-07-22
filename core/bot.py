import os                       # for loading .env file
from dotenv import load_dotenv  # for parsing .env file
import telebot
from telebot import types
from core.actions import get_collage, load_image # all buttons processors
from core.common import *   # bot
from database import *      # init popular tags

load_dotenv(r'E:\портфолио студента\материалы\2024 - 2025\events\summer\collage bot\config.env')
BOT_API_KEY = os.getenv('BOT_API_KEY')

bot = telebot.TeleBot(BOT_API_KEY)  # generates bot entity

# once initialize keyboard as global scoped
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

MAKE_COLLAGE = "Составить коллаж"
LOAD_IMAGE = "Загрузить изображение"

get_collage_action = types.KeyboardButton(MAKE_COLLAGE)
load_image_action = types.KeyboardButton(LOAD_IMAGE)

markup.add(get_collage_action, load_image_action)
# TODO: optionally we can add info_action, which send links to us repo and all that ...


# once initialize inline buttons block
POPULAR_TAGS        = ["#derpy"]    # TODO: DB response @JaneeWaterlemonka
choose_board        = types.InlineKeyboardMarkup([[types.InlineKeyboardButton("#derpy", callback_data="#derpy")]]) # TODO: DB response @JaneeWaterlemonka


# global dialog context for handlers
DIALOG_MODE         = 'private'
IS_WAITING_IMAGE    = False
IS_WAITING_TAGS     = False
PURPOSES = ["load_image", "get_collage"]    # enumerator
CURRENT_REQUEST = "chill"                   # contains enumerator's value

@bot.message_handler(commands=['start'])
def welcome(message) -> None:
    '''
    Here we can use stickers and all that ...
    and action buttons like:
    info = types.KeyboardButton('About Us')
    :param message: telebot.types.Message
    :return: None
    '''
    bot.send_message(message.chat.id,
                     HELLO_MSG, # common.py::
                     reply_markup=markup,
                     parse_mode='html')


@bot.message_handler(content_types=["text"])
def start_send_messages(message) -> None:
    '''
    Here processing response depending on user's request
    :param message: telebot.types.Message
    :return: None
    '''
    global IS_WAITING_IMAGE, IS_WAITING_TAGS, PURPOSES, CURRENT_REQUEST

    if message.chat.type == DIALOG_MODE:
        prompt = message.text

        if IS_WAITING_TAGS: #bot waiting tags for loading photo

            if CURRENT_REQUEST == PURPOSES[0]:
                answer  = load_image.process(message)

                if load_image.is_ok():
                    IS_WAITING_TAGS = False
                else:
                    answer = user_mistake_msg()  # common.py::

            elif CURRENT_REQUEST == PURPOSES[1]:    # get collage action branch
                answer  = get_collage.process(message)
                photo   = get_collage.get_instance()
                bot.send_photo(message.chat.id,
                               photo)  # sending photo as byte array

                if get_collage.is_ok():
                    IS_WAITING_TAGS = False
                else:
                    answer = user_mistake_msg()  # common.py::

            else:
                print(f"something went wrong, undefined request from {message.chat.id}")
                answer = "Упси Вупси, я ошибся ((\n"
                answer += user_mistake_msg()

        else:
            if prompt == MAKE_COLLAGE:
                answer = LOAD_IMAGE_TAGS_PLS_MSG # TODO: GET_COLLAGE_TAGS_PLS_MSG @topShizoid2010
                IS_WAITING_TAGS = True # set dialog context
                CURRENT_REQUEST = PURPOSES[1]

                bot.send_message(message.chat.id,
                                 answer,
                                 reply_markup=choose_board,
                                 parse_mode='html')  # every answer sending as html text
                return

            elif prompt == LOAD_IMAGE:
                answer = LOAD_IMAGE_MANUAL_MSG
                IS_WAITING_IMAGE = True # set dialog context
                CURRENT_REQUEST = PURPOSES[0]

            else:
                answer = UNEXPECTED_TEXT_MSG

        bot.send_message(message.chat.id,
                         answer,
                         parse_mode='html') # every answer sending as html text

    else:
        print(f"something went wrong, non expected chat type from {message.chat.id}")


@bot.message_handler(content_types=['photo'])   # answer to all photos
def photo_send_message(message) -> None:
    '''
    This handler tracking all sended photos
    depending on context
    :param message: telebot.types.Message
    :return: None
    '''
    global IS_WAITING_IMAGE, IS_WAITING_TAGS

    if IS_WAITING_IMAGE:
        ok = load_image.save_to_buffer(message.photo)

        if ok:
            IS_WAITING_IMAGE    = False    # reset dialog context
            IS_WAITING_TAGS     = True
            answer = LOAD_IMAGE_TAGS_PLS_MSG

        else:
            print(f"something went wrong, failed to save image buffer from {message.chat.id}")
            answer = r"""Упси Вупси, я ошибся ((\n""" # TODO: @topShizoid2010

    else:
        # TODO: @TopShizoid2010, make help message, please, 'html' or 'markdown' too:
        answer = '''
            Here located @TopShizoid2010's help message
            You can set parse mode: 'html' or 'markdown' maybe
            '''

    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=markup,
                     parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data in POPULAR_TAGS)
def inline_buttons_handler(call):
    global IS_WAITING_TAGS, CURRENT_REQUEST, PURPOSES

    try:
        if call.message:
            if call.data in POPULAR_TAGS:
                IS_WAITING_TAGS = True          # set dialog context
                CURRENT_REQUEST = PURPOSES[1]   # get collage

                start_send_messages(call.message)
                bot.answer_callback_query(call.id)
                return

        print(f"something went wrong, failed to save image buffer from {call.message.chat.id}")
        raise RuntimeError("inline button callback crashed")

    except Exception as e:
        print(f"something went wrong, failed to save image buffer from {call.message.chat.id}")
        print(e)
        bot.send_message(call.message.chat.id,
                         r'''
                         @topShizoid2010, make error message for inline button response
                         ''',
                         parse_mode='html')

# vvv RUNNING vvv
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Network error: ', e)
    except Exception as r:
        print("Unexpected error: ", r)
    finally:
        print("running finished")