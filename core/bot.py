import os                       # for loading .env file
from dotenv import load_dotenv  # for parsing .env file
import telebot
from telebot import types
from core.database import get_most_popular_tags
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
POPULAR_TAGS        = get_most_popular_tags()
choose_board        = get_collage.get_inline_markup()


# initialize DB once (IF NOT EXIST)
init_db()


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