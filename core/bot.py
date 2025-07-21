import os                       # for loading .env file
from dotenv import load_dotenv  # for parsing .env file
import telebot
from telebot import types
from core.actions import get_collage, load_image # all buttons processors

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


# global dialog context for photo handler
IS_WAITING_IMAGE = False

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
                     '''
                     Here located @TopShizoid2010's message
                     You can set parse mode: 'html' or 'markdown' maybe
                     ''',
                     reply_markup=markup)


@bot.message_handler(content_types=["text"])
def start_send_messages(message) -> None:
    '''
    Here processing response depending on user's request
    :param message: telebot.types.Message
    :return: None
    '''
    global IS_WAITING_IMAGE

    if message.chat.type == 'private':
        prompt = message.text
        photo = ''  # will be byte array raw data vvv

        if prompt == MAKE_COLLAGE:
            answer = get_collage.help(message)
            answer += get_collage.process(message)
            photo = get_collage.get_instance()
            bot.send_photo(message.chat.id,
                           photo)  # sending photo as byte array

        elif prompt == LOAD_IMAGE:
            answer = load_image.help(message)
            IS_WAITING_IMAGE = True # set dialog context

        else:
            # TODO: TopShizoid2010, change it maybe:
            answer = "Пожалуйста, используйте кнопки, я не понимаю команду"

        bot.send_message(message.chat.id,
                         answer) # every answer sending as .md text

    else:
        # TODO: send diagnostics log
        pass


@bot.message_handler(content_types=['photo'])   # answer to all photos
def photo_send_message(message) -> None:
    '''
    This handler tracking all sended photos
    depending on context
    :param message: telebot.types.Message
    :return: None
    '''
    global IS_WAITING_IMAGE

    if IS_WAITING_IMAGE:
        answer = load_image.process(message)
        IS_WAITING_IMAGE = False    # reset dialog context

    else:
        # TODO: @TopShizoid, make help message, please, 'html' or 'markdown' too:
        answer = '''
            Here located @TopShizoid2010's help message
            You can set parse mode: 'html' or 'markdown' maybe
            '''

    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=markup)


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