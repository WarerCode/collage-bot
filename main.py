import os                       # for loading .env file
from dotenv import load_dotenv  # for parsing .env file
import telebot
from telebot import types

load_dotenv(dotenv_path='config.env')
BOT_API_KEY = os.getenv('BOT_API_KEY')

bot = telebot.TeleBot(BOT_API_KEY)  # generates bot entity


@bot.message_handler(commands=['start', 'get_image', 'load_image'])
def wellcome(message) -> None:
    '''
    Here will be inited wellcome message
    Here we can use stickers and all that ...
    and action buttons like:
    info = types.KeyboardButton('About Us')
    :param message: telebot.types.Message
    :return: None
    '''
    pass


@bot.message_handler(content_types=["text"])    # only for text message ?
def start_send_messages(message) -> None:
    '''
    Here processing response depending on user's request
    :param message: telebot.types.Message
    :return: None
    '''
    pass

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