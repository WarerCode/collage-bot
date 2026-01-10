"""
Основной класс бота для управления коллажами с интеграцией платежной системы.

Реализует:
- Обработку команд и сообщений от пользователей
- Управление состоянием пользователя (FSM)
- Создание и обработку коллажей
- Интеграцию с платежной системой Telegram Stars
- Работу с медиа-контентом
"""

import os
import logging
import typing
import enum
import json
from datetime import datetime
from io import BytesIO

import dotenv
import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.custom_filters import StateFilter

import core.warerobjects.content_types.image as content_image
import core.warerobjects.content_types.collage as collage_module
import core.warerobjects.politics.size_policy as size_policy
import core.warerobjects.management.database as database
import core.warerobjects.management.pay_manager as pay_manager
import core.warerobjects.data.userinfo as userinfo
import core.user as collage_user

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CollageStates(StatesGroup):
    """Состояния конечного автомата бота."""
    waiting_for_images = State()
    selecting_size = State()
    selecting_effects = State()
    processing_collage = State()

class CollageBot:
    """
    Основной класс бота для создания коллажей.
    
    Атрибуты:
        bot: экземпляр TeleBot
        db: объект базы данных
        payment_manager: менеджер платежей и подписок
        user_images: временное хранилище изображений пользователей
        user_collage_data: временное хранилище данных коллажей
    """
    
    def __init__(self, token: str):
        """
        Инициализация бота.
        
        Аргументы:
            token (str): токен бота от BotFather
        """
        # Инициализация компонентов
        self.bot = telebot.TeleBot(token)
        self.db = self._init_database()
        self.payment_manager = pay_manager.PaymentManager(self.db, self.bot)
        self.users_cache = collage_user.UserCache()
        
        # Временные хранилища
        self.user_images = {}  # user_id -> list[content_image.Image]
        self.user_collage_data = {}  # user_id -> dict с данными для коллажа
        
        # Регистрация обработчиков
        self._register_handlers()
        self._register_custom_filters()
    
    def _init_database(self) -> database.Database:
        """Инициализация подключения к базе данных."""
        return database.Database(
            database.DBTypes.POSTGRESQL,
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    
    def _wrap_handler(self, handler):
        def wrapper(message: telebot.types.Message):
            print(message.from_user.to_dict())
            user = database.ensure_user_exists(self.db, message.from_user, self.users_cache)
            self.users_cache.update_user(message.from_user.id, user)
            return handler(message)
        return wrapper
        
    def _register_custom_filters(self):
        """Регистрация кастомных фильтров."""
        self.bot.add_custom_filter(StateFilter(self.bot))
    
    def _register_handlers(self):
        """Регистрация всех обработчиков команд и сообщений."""
        # Основные команды
        self.bot.message_handler(commands=['start'])(self._wrap_handler(self._start_command))
        self.bot.message_handler(commands=['help'])(self._wrap_handler(self._help_command))
        self.bot.message_handler(commands=['subscription'])(self._wrap_handler(self._subscription_command))
        self.bot.message_handler(commands=['history'])(self._wrap_handler(self._history_command))
        self.bot.message_handler(commands=['collage'])(self._wrap_handler(self._collage_command))
        self.bot.message_handler(commands=['cancel'])(self._wrap_handler(self._cancel_command))
        
        # Обработчики состояний
        self.bot.message_handler(
            content_types=['photo'], 
            state=CollageStates.waiting_for_images
        )(self._wrap_handler(self._handle_image_input))
        
        self.bot.message_handler(
            content_types=['text'],
            state=CollageStates.waiting_for_images
        )(self._wrap_handler(self._handle_text_input))
        
        # Обработчики callback-запросов
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('size_'))(self._wrap_handler(self._handle_size_selection))
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('effect_'))(self._wrap_handler(self._handle_effect_selection))
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('payment_'))(self._wrap_handler(self._handle_payment_callback))
        self.bot.callback_query_handler(func=lambda call: call.data == 'process_collage')(self._wrap_handler(self._process_collage))
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_sizes')(self._wrap_handler(self._handle_back_to_sizes))
        self.bot.callback_query_handler(func=lambda call: call.data == 'cancel_collage')(self._wrap_handler(self._cancel_command))
        
        # Обработчики платежей
        self.bot.pre_checkout_query_handler(func=lambda query: True)(self.payment_manager.handle_pre_checkout_query)
        self.bot.message_handler(content_types=['successful_payment'])(self._wrap_handler(self._handle_successful_payment))
        
        # Обработчик неизвестных команд
        self.bot.message_handler(func=lambda message: True)(self._wrap_handler(self._handle_unknown_command))
    
    def _start_command(self, message: telebot.types.Message):
        """Обработчик команды /start."""
        user = message.from_user
        
        # Регистрация пользователя в базе данных
        self._register_user(user)
        
        # Приветственное сообщение
        welcome_text = (
            f"👋 Привет, {user.first_name}!\n\n"
            "Я бот для создания красивых коллажей из твоих фотографий.\n\n"
            "📸 <b>Что я умею:</b>\n"
            "• Создавать коллажи из нескольких фото\n"
            "• Применять различные эффекты и рамки\n"
            "• Настраивать размер и пропорции\n"
            "• Работать с подписками\n\n"
            "🚀 <b>Начни с команды /collage</b> чтобы создать свой первый коллаж!\n\n"
            "❓ Помощь: /help\n"
            "💎 Подписка: /subscription"
        )
        
        keyboard = [
            [telebot.types.InlineKeyboardButton("🎨 Создать коллаж", callback_data="collage_start")],
            [telebot.types.InlineKeyboardButton("💎 Моя подписка", callback_data="subscription_info"),
             telebot.types.InlineKeyboardButton("📊 История платежей", callback_data="payment_history")],
            [telebot.types.InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = telebot.types.InlineKeyboardMarkup(keyboard)
        
        self.bot.send_message(
            chat_id=message.chat.id,
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        self.bot.set_state(user.id, CollageStates.waiting_for_images)
    
    def _help_command(self, message: telebot.types.Message):
        """Обработчик команды /help."""
        help_text = (
            "📖 <b>Справка по командам:</b>\n\n"
            "🎨 <b>/collage</b> - создать новый коллаж\n"
            "• Загрузите несколько фотографий\n"
            "• Выберите размер и эффекты\n"
            "• Получите готовый коллаж!\n\n"
            "💎 <b>/subscription</b> - управление подпиской\n"
            "• Проверка статуса подписки\n"
            "• Покупка/продление подписки\n"
            "• Информация о тарифах\n\n"
            "📊 <b>/history</b> - история платежей\n\n"
            "❓ <b>/help</b> - эта справка\n\n"
            "<b>Как создать коллаж:</b>\n"
            "1. Отправьте команду /collage\n"
            "2. Загрузите от 2 до 10 фотографий\n"
            "3. Выберите размер коллажа\n"
            "4. Выберите эффекты (опционально)\n"
            "5. Получите готовый коллаж!\n\n"
            "💡 <b>Совет:</b> Для лучшего качества используйте фотографии схожего размера."
        )
        
        self.bot.reply_to(message, help_text, parse_mode='HTML')
    
    def _collage_command(self, message: telebot.types.Message):
        """Обработчик команды /collage - начало создания коллажа."""
        user = message.from_user
        
        # Проверяем лимиты для бесплатных пользователей
        subscription_status = self.payment_manager.check_subscription_status(user.id)
        if not subscription_status.get('has_subscription', False):
            # Проверяем дневной лимит бесплатных коллажей
            free_collages_remaining = self._get_free_collages_remaining(user.id)
            if free_collages_remaining <= 0:
                self._show_limits_exceeded(message)
                return
        
        # Сбрасываем предыдущие данные
        self.user_images[user.id] = []
        self.user_collage_data[user.id] = {}
        
        instruction_text = (
            "🎨 <b>Создание коллажа</b>\n\n"
            "📸 <b>Шаг 1: Загрузка фотографий</b>\n"
            "Отправьте мне от 2 до 10 фотографий.\n\n"
            "💡 <b>Рекомендации:</b>\n"
            "• Используйте фото схожего размера\n"
            "• Максимальное качество - лучший результат\n"
            "• Можно отправлять по одной или группой\n\n"
            "📎 <b>Отправьте фотографии сейчас...</b>\n\n"
            "❌ Для отмены используйте /cancel"
        )
        
        self.bot.send_message(
            chat_id=message.chat.id,
            text=instruction_text,
            parse_mode='HTML'
        )
        
        self.bot.set_state(user.id, CollageStates.waiting_for_images)
    
    def _handle_image_input(self, message: telebot.types.Message):
        """Обработка загружаемых изображений."""
        user = message.from_user
        
        if user.id not in self.user_images:
            self.user_images[user.id] = []
        
        try:
            # Получаем самое качественное изображение
            photo = message.photo[-1] if message.photo else None
            if not photo:
                self.bot.reply_to(message, "❌ Пожалуйста, отправьте фотографию.")
                return
            
            # Скачиваем изображение
            file_info = self.bot.get_file(photo.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            
            # Создаем объект Image из bytes
            image_obj = content_image.Image(image=downloaded_file)
            self.user_images[user.id].append(image_obj)
            
            # Показываем прогресс
            images_count = len(self.user_images[user.id])
            progress_text = (
                f"📸 Загружено фотографий: {images_count}/10\n\n"
                f"✅ Фото #{images_count} успешно добавлено!\n\n"
            )
            
            if images_count >= 2:
                progress_text += "🔄 <b>Можно загружать еще или перейти к выбору размера:</b>"
                
                keyboard = [
                    [telebot.types.InlineKeyboardButton("➡️ Выбрать размер", callback_data="size_selection")],
                    [telebot.types.InlineKeyboardButton("❌ Отменить", callback_data="cancel_collage")]
                ]
                reply_markup = telebot.types.InlineKeyboardMarkup(keyboard)
            else:
                progress_text += "📎 <b>Отправьте еще хотя бы одну фотографию...</b>"
                reply_markup = None
            
            self.bot.send_message(
                chat_id=message.chat.id,
                text=progress_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            # Если достигли максимума, переходим к выбору размера
            if images_count >= 10:
                self._show_size_selection(message)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.bot.reply_to(message, "❌ Ошибка при обработке фотографии. Попробуйте еще раз.")
    
    def _handle_text_input(self, message: telebot.types.Message):
        """Обработка текстового ввода в состоянии ожидания изображений."""
        if message.text == '/cancel':
            return self._cancel_command(message)
            
        self.bot.reply_to(
            message,
            "📎 Пожалуйста, отправьте фотографии для создания коллажа.\n"
            "Или используйте /cancel для отмены."
        )
    
    def _show_size_selection(self, message: telebot.types.Message = None, call: telebot.types.CallbackQuery = None):
        """Показ выбора размера коллажа."""
        chat_id = message.chat.id if message else call.message.chat.id
        message_id = call.message.message_id if call else None
        
        size_text = (
            "📐 <b>Выбор размера коллажа</b>\n\n"
            "Выберите подходящий размер и пропорции для вашего коллажа:\n\n"
            "• ⬜ <b>Квадратный</b> - 1:1, идеально для Instagram\n"
            "• 📱 <b>Вертикальный</b> - 3:4, для сторис и постов\n"
            "• 🖥️ <b>Горизонтальный</b> - 4:3, для компьютеров\n"
            "• 🎬 <b>Широкий</b> - 16:9, для обоев и презентаций"
        )
        
        keyboard = [
            [telebot.types.InlineKeyboardButton("⬜ Квадратный", callback_data="size_square")],
            [telebot.types.InlineKeyboardButton("📱 Вертикальный", callback_data="size_vertical")],
            [telebot.types.InlineKeyboardButton("🖥️ Горизонтальный", callback_data="size_horizontal")],
            [telebot.types.InlineKeyboardButton("🎬 Широкий", callback_data="size_wide")],
            [telebot.types.InlineKeyboardButton("❌ Отменить", callback_data="cancel_collage")]
        ]
        reply_markup = telebot.types.InlineKeyboardMarkup(keyboard)
        
        if call:
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=size_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            self.bot.send_message(
                chat_id=chat_id,
                text=size_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        
        self.bot.set_state(chat_id, CollageStates.selecting_size)
    
    def _handle_size_selection(self, call: telebot.types.CallbackQuery):
        """Обработка выбора размера коллажа."""
        user = call.from_user
        size_type = call.data.replace("size_", "")
        
        # Сохраняем выбранный размер
        self.user_collage_data[user.id] = {
            'size_policy': self._get_size_policy(size_type),
            'effects': []
        }
        
        # Показываем выбор эффектов
        effects_text = (
            "🎨 <b>Выбор эффектов для коллажа</b>\n\n"
            "Вы можете применить различные эффекты и рамки к вашему коллажу:\n\n"
            "• 🖼️ Рамки разных стилей\n"
            "• 🌈 Цветовые фильтры\n"
            "• ⚡ Специальные эффекты\n\n"
            "Выберите эффекты ниже:"
        )
        
        keyboard = [
            [telebot.types.InlineKeyboardButton("🍃 Лиственная рамка", callback_data="effect_leaves")],
            [telebot.types.InlineKeyboardButton("🏰 Готическая рамка", callback_data="effect_gothic")],
            [telebot.types.InlineKeyboardButton("⬜ Простая рамка", callback_data="effect_plain")],
            [telebot.types.InlineKeyboardButton("⚫ Черно-белый", callback_data="effect_bw")],
            [telebot.types.InlineKeyboardButton("🔘 Без эффектов", callback_data="effect_none")],
            [telebot.types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_sizes"),
             telebot.types.InlineKeyboardButton("🚀 Создать!", callback_data="process_collage")]
        ]
        reply_markup = telebot.types.InlineKeyboardMarkup(keyboard)
        
        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=effects_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        self.bot.set_state(user.id, CollageStates.selecting_effects)
    
    def _handle_effect_selection(self, call: telebot.types.CallbackQuery):
        """Обработка выбора эффектов."""
        user = call.from_user
        effect_type = call.data.replace("effect_", "")
        
        if effect_type == "none":
            self.user_collage_data[user.id]['effects'] = []
            self.bot.answer_callback_query(call.id, "✅ Эффекты отключены")
            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="✅ Эффекты отключены. Нажмите 'Создать!' для генерации коллажа.",
                parse_mode='HTML'
            )
        else:
            # Добавляем эффект в список
            if 'effects' not in self.user_collage_data[user.id]:
                self.user_collage_data[user.id]['effects'] = []
            
            self.user_collage_data[user.id]['effects'].append(effect_type)
            self.bot.answer_callback_query(call.id, f"✅ Эффект '{effect_type}' добавлен")
    
    def _process_collage(self, call: telebot.types.CallbackQuery):
        """Создание и отправка коллажа."""
        user = call.from_user
        
        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔄 <b>Создаю ваш коллаж...</b>\n\nЭто займет несколько секунд ⏳",
            parse_mode='HTML'
        )
        
        try:
            # Создаем коллаж
            collage = collage_module.Collage(list_of_images=self.user_images[user.id])
            
            collage_data = self.user_collage_data[user.id]
            size_policy = collage_data['size_policy']
            effects = collage_data.get('effects', [])
            
            # Применяем эффекты если есть
            effects_data = []
            for effect in effects:
                effects_data.append({
                    "effect": effect,
                    "kwargs": {"shape": size_policy.size.value}
                })
            
            # Создаем коллаж
            result_image = collage.create_collage(
                size_policy=size_policy,
                effects_data=effects_data if effects else None
            )
            
            # Конвертируем в bytes для отправки
            img_byte_arr = BytesIO()
            result_image.image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # Отправляем коллаж пользователю
            self.bot.send_photo(
                chat_id=user.id,
                photo=img_byte_arr.getvalue(),
                caption="🎉 <b>Ваш коллаж готов!</b>\n\n"
                       "Понравился результат? Создайте еще один коллаж с помощью /collage",
                parse_mode='HTML'
            )
            
            # Очищаем временные данные
            self._cleanup_user_data(user.id)
            self.bot.delete_state(user.id)
            
            # Обновляем статистику пользователя
            self._update_user_collage_stats(user.id)
            
        except Exception as e:
            logger.error(f"Error creating collage: {e}")
            self.bot.send_message(
                chat_id=user.id,
                text="❌ <b>Произошла ошибка при создании коллажа</b>\n\n"
                     "Попробуйте еще раз или используйте другие фотографии.",
                parse_mode='HTML'
            )
    
    def _subscription_command(self, message: telebot.types.Message):
        """Обработчик команды /subscription."""
        user = message.from_user
        
        subscription_status = True
        # subscription_status = self.payment_manager.check_subscription_status(user.id)
        
        if False and subscription_status.get('has_subscription', False) and subscription_status.get('is_active', False):
            # Показываем информацию о текущей подписке
            days_remaining = subscription_status.get('days_remaining', 0)
            plan_name = subscription_status.get('plan', '').capitalize()
            
            subscription_text = (
                f"💎 <b>Ваша подписка: {plan_name}</b>\n\n"
                f"✅ Статус: <b>Активна</b>\n"
                f"📅 Осталось дней: <b>{days_remaining}</b>\n"
                f"🎨 Доступно коллажей: <b>Безлимит</b>\n\n"
                f"Спасибо за использование премиум-функций! 🚀"
            )
            self.bot.reply_to(message, subscription_text, parse_mode='HTML')
        else:
            # Предлагаем купить подписку
            subscription_text = (
                "💎 <b>Премиум подписка</b>\n\n"
                "🔓 <b>Откройте все возможности:</b>\n"
                "• 🎨 Безлимитное создание коллажей\n"
                "• ⚡ Приоритетная обработка\n"
                "• 🖼️ Эксклюзивные эффекты и рамки\n"
                "• 📈 Улучшенное качество\n\n"
                "💳 <b>Тарифы:</b>\n"
                "• Basic - 100 звезд/месяц\n"
                "• Premium - 300 звезд/месяц  \n"
                "• Pro - 500 звезд/месяц\n\n"
                "Выберите тариф для покупки:"
            )
            
            keyboard = [
                [telebot.types.InlineKeyboardButton("Basic - 100 ⭐", callback_data="payment_basic")],
                [telebot.types.InlineKeyboardButton("Premium - 300 ⭐", callback_data="payment_premium")],
                [telebot.types.InlineKeyboardButton("Pro - 500 ⭐", callback_data="payment_pro")],
                [telebot.types.InlineKeyboardButton("📊 История платежей", callback_data="payment_history")]
            ]
            reply_markup = telebot.types.InlineKeyboardMarkup(keyboard)
            
            self.bot.reply_to(
                message,
                text=subscription_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    def _handle_payment_callback(self, call: telebot.types.CallbackQuery):
        """Обработка callback'ов от кнопок платежей."""
        user = call.from_user
        action = call.data.replace("payment_", "")
        
        if action in ["basic", "premium", "pro"]:
            plan = database.SubscriptionPlan[action.upper()]
            result = self.payment_manager.create_subscription_invoice(user.id, plan, call.message.chat.id)
            print(result)
            
            if result["success"]:
                self.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"💎 <b>Подписка {plan.value.capitalize()}</b>\n\n"
                         f"Стоимость: {self.payment_manager.SUBSCRIPTION_PRICES[plan]} ⭐\n\n"
                         f"Для оплаты используйте кнопку ниже:",
                    parse_mode='HTML'
                )
            else:
                self.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="❌ Ошибка при создании платежа. Попробуйте позже.",
                    parse_mode='HTML'
                )
        elif action == "history":
            self._history_command(call.message)
    
    def _handle_successful_payment(self, message: telebot.types.Message):
        """Обработка успешного платежа."""
        print("In _handle_successful_payment")
        user = message.from_user
        successful_payment = message.successful_payment
        
        result = self.payment_manager.handle_successful_payment(user.id, successful_payment)
        print(result)
        
        if result["success"]:
            if os.getenv("DEBUG") == "True":
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text="🎉 [DEBUG] Подписка успешно активирована!"
                )
            else:
                self.bot.reply_to(
                    message,
                    f"🎉 <b>Поздравляем!</b>\n\n"
                    f"Подписка {result['plan']} успешно активирована!\n"
                    f"Действует до: {result['end_date'][:10]}\n\n"
                    f"Теперь вам доступны все премиум-функции! 🚀",
                    parse_mode='HTML'
                )
        else:
            if os.getenv("DEBUG") == "True":
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text="🎉 [DEBUG] Подписка НЕ активирована!"
                )
            else:
                self.bot.reply_to(
                    message,
                    "❌ Произошла ошибка при активации подписки. "
                    "Свяжитесь с поддержкой.",
                    parse_mode='HTML'
                )
    
    def _handle_pre_checkout(self, query: telebot.types.PreCheckoutQuery):
        """Обработка pre-checkout запроса."""
        # Всегда подтверждаем запрос (в реальном боте нужно добавить валидацию)
        self.bot.answer_pre_checkout_query(query.id, ok=True)
    
    def _history_command(self, message: telebot.types.Message):
        """Обработчик команды /history - история платежей."""
        user = message.from_user
        
        payments_history = self.payment_manager.get_user_payments(user.id)
        
        if payments_history["success"] and payments_history["payments"]:
            history_text = "📊 <b>История платежей</b>\n\n"
            
            for payment in payments_history["payments"][:5]:  # Последние 5 платежей
                status_emoji = "✅" if payment["status"] == "completed" else "❌"
                history_text += (
                    f"{status_emoji} <b>{payment['subscription'] or 'Платеж'}</b>\n"
                    f"💎 {payment['amount']} {payment['currency']} • "
                    f"{payment['created_at'][:10]}\n"
                    f"Статус: {payment['status']}\n\n"
                )
        else:
            history_text = "📊 <b>История платежей</b>\n\nУ вас еще не было платежей."
        
        self.bot.reply_to(message, history_text, parse_mode='HTML')
    
    def _cancel_command(self, message: telebot.types.Message = None, call: telebot.types.CallbackQuery = None):
        """Обработчик команды отмены."""
        if call:
            user = call.from_user
            chat_id = call.message.chat.id
            self.bot.answer_callback_query(call.id, "Операция отменена")
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="❌ Операция отменена.",
                parse_mode='HTML'
            )
        else:
            user = message.from_user
            self.bot.reply_to(message, "❌ Операция отменена.")
        
        self._cleanup_user_data(user.id)
        self.bot.delete_state(user.id)
    
    def _handle_back_to_sizes(self, call: telebot.types.CallbackQuery):
        """Обработка возврата к выбору размеров."""
        self._show_size_selection(call=call)
    
    def _handle_unknown_command(self, message: telebot.types.Message):
        """Обработка неизвестных команд."""
        if message.text.startswith('/'):
            self.bot.reply_to(
                message,
                "🤔 Не понимаю эту команду. Используйте /help для справки."
            )
    
    # Вспомогательные методы
    
    def _cleanup_user_data(self, user_id: int):
        """Очистка временных данных пользователя."""
        self.user_images.pop(user_id, None)
        self.user_collage_data.pop(user_id, None)
    
    def _get_size_policy(self, size_type: str) -> size_policy.SizePolicy:
        """Получение политики размера по типу."""
        size_mapping = {
            "square": size_policy.SizePolicy.Size.SQUARE,
            "vertical": size_policy.SizePolicy.Size.VERTICAL, 
            "horizontal": size_policy.SizePolicy.Size.HORIZONTAL,
            "wide": size_policy.SizePolicy.Size.WIDE
        }
        return size_policy.SizePolicy(size_mapping.get(size_type, size_policy.SizePolicy.Size.SQUARE))
    
    def _register_user(self, user):
        """Регистрация пользователя в базе данных."""
        # Здесь должна быть реализация регистрации пользователя
        # Используйте BaseQueries для вставки в таблицу users
        pass
    
    def _get_free_collages_remaining(self, user_id: int) -> int:
        """Получение количества оставшихся бесплатных коллажей."""
        # Реализация проверки лимитов
        return 3  # Заглушка
    
    def _update_user_collage_stats(self, user_id: int):
        """Обновление статистики пользователя после создания коллажа."""
        # Реализация обновления статистики
        pass
    
    def _show_limits_exceeded(self, message: telebot.types.Message):
        """Показ сообщения о превышении лимитов."""
        limit_text = (
            "❌ <b>Лимит бесплатных коллажей исчерпан</b>\n\n"
            "Вы создали максимальное количество коллажей для бесплатного тарифа.\n\n"
            "💎 <b>Премиум подписка</b> открывает:\n"
            "• 🎨 Безлимитное создание коллажей\n"  
            "• ⚡ Приоритетную обработку\n"
            "• 🖼️ Эксклюзивные эффекты\n\n"
            "Используйте /subscription для покупки подписки!"
        )
        
        self.bot.reply_to(message, limit_text, parse_mode='HTML')
    
    def run(self):
        """Запуск бота."""
        logger.info("Бот запущен")
        self.bot.infinity_polling()
    
    def __str__(self):
        return f"CollageBot(active_users={len(self.user_images)})"
    
    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    # Загрузка переменных окружения
    dotenv.load_dotenv("dev.env")

    # Запуск бота
    bot = CollageBot(os.getenv("BOT_API_KEY"))
    bot.run()