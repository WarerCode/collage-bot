import telebot
from telebot import types
import os
from dotenv import load_dotenv
from serializers import list_to_str

load_dotenv("./.env")

BOT_API_KEY = os.getenv("BOT_API_KEY")

bot = telebot.TeleBot(BOT_API_KEY)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton("Загрузить изображение"))
keyboard.add(types.KeyboardButton("Получить коллаж"))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Выберите действие:",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda m: m.text == "Загрузить изображение")
def request_image(message):
    bot.send_message(
        message.chat.id,
        "Отправьте изображение для загрузки."
    )
    bot.register_next_step_handler(message, handle_uploaded_image)

def handle_uploaded_image(message):
    try:
        if message.content_type != 'photo':
            raise ValueError("Это не изображение")

        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        os.makedirs("images", exist_ok=True)
        file_path = f"images/{file_id}.jpg"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.send_message(message.chat.id, "Придумайте теги для изображения! (testing)")

        bot.register_next_step_handler(message, handle_send_image_tags)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка: {e} (testing)")

def handle_send_image_tags(message):
    if message.content_type != "text":
        raise ValueError("Это не теги")
    
    tags = set(tag for tag in message.text.lower().replace("#", "").split() if tag)
    tags_str = list_to_str(tags)
    print(tags_str)

    bot.send_message(message.chat.id, "Изображение с тегами успешно загружено")



if __name__ == '__main__':
    print("Бот запущен")
    bot.infinity_polling()