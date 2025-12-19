"""
Менеджер платежей и подписок для Telegram бота, соответствующий официальному Bot API для Telegram Stars.

Основные возможности:
- Создание счетов (инвойсов) через sendInvoice и createInvoiceLink.
- Обработка предварительных проверок (pre-checkout) и успешных платежей.
- Управление подписками на основе разовых платежей.
- Возврат средств (refund).
"""
import datetime
import json
import os
import typing
import enum
from decimal import Decimal
import telebot
import dotenv

import core.warerobjects.warerobject as warer
import core.warerobjects.data.userinfo as userinfo
import core.warerobjects.management.database as database

class PaymentType(enum.Enum):
    """Планы подписок с ценами в Telegram Stars."""
    SUBSCRIPTION = "subscription"

class PaymentStatus(enum.Enum):
    """Статусы платежей в системе."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentCurrency(enum.Enum):
    """Статусы платежей в системе."""
    STARS = "XTR"

class PaymentMethod(enum.Enum):
    """Статусы платежей в системе."""
    STARS = "stars"

class PaymentManager(warer.WarerObject):
    """
    Менеджер платежей, реализующий логику в соответствии с Telegram Bot API.
    """
    
    # Цены подписок в Telegram Stars (XTR)
    SUBSCRIPTION_PRICES = {
        database.SubscriptionPlan.BASIC: 100,
        database.SubscriptionPlan.PREMIUM: 300,
        database.SubscriptionPlan.PRO: 500,
    }
    
    # Длительности подписок в днях (логика приложения, не API)
    SUBSCRIPTION_DURATIONS = {
        database.SubscriptionPlan.BASIC: 30,
        database.SubscriptionPlan.PREMIUM: 30,  
        database.SubscriptionPlan.PRO: 30,
    }

    def __init__(self, database: database.Database, bot: telebot.TeleBot):
        """
        Инициализация менеджера платежей.
        
        Аргументы:
            database (database.Database): объект базы данных
            bot_token (str): токен бота от BotFather
        """
        super().__init__()
        self.db = database
        self.bot = bot

    def _create_fake_pre_checkout_query(
            self, 
            user_id: str,
            currency: str,
            amount: float,
            payload: typing.Dict,
        ):
        try:
            pre_checkout_query = telebot.types.PreCheckoutQuery(
                id="test_pre_checkout_id",
                from_user=telebot.types.User(
                    id=user_id,
                    is_bot=False,
                    first_name="Test"
                ),
                currency=currency,
                total_amount=amount,
                invoice_payload=payload
            )

            update = telebot.types.Update(
                update_id=123456,
                message=None,
                edited_message=None,
                channel_post=None,
                edited_channel_post=None,
                inline_query=None,
                chosen_inline_result=None,
                callback_query=None,
                shipping_query=None,
                pre_checkout_query=pre_checkout_query,
                poll=None,
                poll_answer=None,
                my_chat_member=None,
                chat_member=None,
                chat_join_request=None,
                message_reaction=None,
                message_reaction_count=None,
                removed_chat_boost=None,
                chat_boost=None,
                business_connection=None,
                business_message=None,
                edited_business_message=None,
                deleted_business_messages=None,
                purchased_paid_media=None,
            )

            new_updates = self.bot.process_new_updates([update])

        except Exception as e:
            print(e)

    def create_subscription_invoice(
            self, 
            user_id: int, 
            plan: database.SubscriptionPlan, 
            chat_id: int = None
        ) -> typing.Dict[str, typing.Any]:
        """
        Создает инвойс для подписки через метод sendInvoice или createInvoiceLink.
        
        Аргументы:
            user_id (int): ID пользователя в вашей системе
            plan (database.SubscriptionPlan): выбранный план подписки
            chat_id (int): опционально, ID чата для отправки инвойса
            
        Возвращает:
            dict: результат создания инвойса
        """
        try:
            # Подготовка данных инвойса в соответствии с Bot API
            title, description = self._get_plan_info(plan)
            
            # Валюта ДОЛЖНА быть "XTR" для Telegram Stars
            currency = PaymentCurrency.STARS.value
            amount = self.SUBSCRIPTION_PRICES[plan]

            subscription_select_query, subscription_select_params = database.BaseQueries.select(
                database.TableNames.SUBSCRIPTIONS.value,
                conditions={"user_id": user_id, "plan_type": plan.value}
            )

            subscription = self.db.fetch_one(subscription_select_query, subscription_select_params)

            if subscription is None:
                subscriptions_insert_query, subscriptions_insert_params = database.BaseQueries.insert(
                    database.TableNames.SUBSCRIPTIONS.value,
                    data={
                        "user_id": user_id, 
                        "plan_type": plan.value
                    }
                )
            
            # Цены должны быть переданы в формате Bot API
            prices = [
                telebot.types.LabeledPrice(
                    label=title,
                    amount=amount,
                )
            ]
            
            # provider_token ДОЛЖЕН быть пустой строкой для цифровых товаров
            provider_token = ""
            
            # Создаем запись о инвойсе в БД
            invoice_data = {
                "user_id": user_id,
                "amount": amount,
                "currency": currency,
                "method": PaymentMethod.STARS.value,
                "status": PaymentStatus.PENDING.value,
                "data": {
                    "plan": plan.value,
                },
            }
            print(invoice_data)
            
            query, params = database.BaseQueries.insert(database.TableNames.PAYMENTS, invoice_data)
            payment = self.db.fetch_one(query, params)

            payload = json.dumps(
                {
                    "payment_id": payment.get("id"), 
                }
            )
            
            if chat_id:
                # Отправляем инвойс прямо в чат
                result = self.bot.send_invoice(
                    chat_id=chat_id,
                    title=title,
                    description=description,
                    invoice_payload=payload,
                    currency=currency,
                    prices=prices,
                    provider_token=provider_token
                )

                if os.getenv("DEBUG") == "True":
                    self._create_fake_pre_checkout_query(
                        user_id=user_id,
                        currency=currency,
                        amount=amount,
                        payload=payload,
                    )
                return {
                    "success": True,
                    "method": "sendInvoice",
                    "result": result,
                    "message": "Инвойс отправлен в чат"
                }
            else:
                # Создаем ссылку на инвойс
                invoice_link = self.bot.send_invoice(
                    title=title,
                    description=description,
                    invoice_payload=payload,
                    currency=currency,
                    prices=prices,
                    provider_token=provider_token
                )
                return {
                    "success": True,
                    "method": "createInvoiceLink", 
                    "result": invoice_link,
                    "message": "Ссылка на инвойс создана"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка создания инвойса"
            }
        
    def handle_pre_checkout_query(self, query: telebot.types.PreCheckoutQuery):
        """Обработка pre-checkout запроса."""
        try:
            print("In handle_pre_checkout_query")
            
            if os.getenv("DEBUG") == "True":
                print("DEBUG MODE → emulating successful_payment")

                now_ts = int(datetime.datetime.now().timestamp())

                message_dict = {
                    "message_id": 999,
                    "date": now_ts,
                    "chat": {
                        "id": query.from_user.id,
                        "type": "private"
                    },
                    "from": {
                        "id": query.from_user.id,
                        "is_bot": False,
                        "first_name": query.from_user.first_name or "Test"
                    },
                    "successful_payment": {
                        "currency": query.currency,
                        "total_amount": query.total_amount,
                        "invoice_payload": query.invoice_payload,
                        "telegram_payment_charge_id": "test_charge_id_123",
                        "provider_payment_charge_id": ""
                    }
                }

                update_dict = {
                    "update_id": 999999,
                    "message": message_dict
                }

                # message = telebot.types.Message.de_json(message_dict)
                update = telebot.types.Update.de_json(update_dict)

                # self.bot.process_new_messages([message])
                self.bot.process_new_updates([update])
                return
    
            # Проверяем возможность обработать заказ
            success = True
            error_message = None

            payload_data = json.loads(query.invoice_payload)
            payment_id = payload_data.get("payment_id")
            select_query, params = database.BaseQueries.select(database.TableNames.PAYMENTS, conditions={"id": payment_id})
            payment = self.db.fetch_one(select_query, params)

            data = payment.get("data", {})
            plan = database.SubscriptionPlan(data.get("plan"))

            user_id = payment.get("user_id")
            amount = payment.get("amount")
            currency = payment.get("currency")
            method = payment.get("method")
            status = payment.get("status")

            if (plan is None or 
                user_id != query.from_user.id or 
                int(amount) != self.SUBSCRIPTION_PRICES[plan] or
                PaymentCurrency(currency) is None or
                PaymentMethod(method) is None or
                PaymentStatus(status) is None
                ):
                success = False
                error_message = "Некорректные данные платежа"
            
            if not success:
                self.bot.answer_pre_checkout_query(
                    query.id, 
                    ok=False,
                    error_message=error_message or "Не удалось обработать заказ"
                )
            else:
                print("In success branch")
                self.bot.answer_pre_checkout_query(
                    query.id, 
                    ok=True
                )
            
        except Exception as e:
            self.bot.answer_pre_checkout_query(
                query.id,
                ok=False, 
                error_message="Внутренняя ошибка сервера"
            )

    def handle_successful_payment(self, user_id: int, successful_payment: telebot.types.SuccessfulPayment) -> typing.Dict[str, typing.Any]:
        """
        Обрабатывает успешный платеж и активирует подписку.
        
        Аргументы:
            user_id (int): ID пользователя
            successful_payment (dict): данные из поля successful_payment апдейта[citation:1]
        """
        try:
            # Извлекаем критически важные данные из платежа
            telegram_payment_charge_id = successful_payment.telegram_payment_charge_id
            total_amount = successful_payment.total_amount

            invoice_payload = json.loads(successful_payment.invoice_payload)
            payment_id = invoice_payload.get("payment_id")
            
            invoice_payload = json.loads(invoice_payload)
            plan = database.SubscriptionPlan(invoice_payload.get("plan"))
            
            # Обновляем запись о платеже в БД
            update_data = {
                "status": PaymentStatus.COMPLETED.value,
                "telegram_payment_charge_id": telegram_payment_charge_id,
                "updated_at": datetime.datetime.now()
            }
            
            query, params = database.BaseQueries.update(
                database.TableNames.PAYMENTS,
                update_data,
                {"id": payment_id, "user_id": user_id}
            )
            self.db.execute(query, params)
            
            # Активируем подписку пользователя
            return self._activate_subscription(user_id, plan, telegram_payment_charge_id)
            
        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка обработки успешного платежа"
            }

    def _activate_subscription(self, user_id: int, plan: database.SubscriptionPlan, 
                             payment_charge_id: str) -> typing.Dict[str, typing.Any]:
        """Активирует подписку пользователя после успешного платежа."""
        try:
            duration_days = self.SUBSCRIPTION_DURATIONS[plan]
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(days=duration_days)
            
            # Создаем запись о подписке
            subscription_data = {
                "user_id": user_id,
                "plan": plan.value,
                "start_date": start_date,
                "end_date": end_date,
                "payment_charge_id": payment_charge_id,
                "is_active": True
            }
            
            # Обновляем статус пользователя
            user_update = {
                userinfo.UserFields.IS_PREMIUM: True,
                userinfo.UserFields.STATUS: "premium",
                userinfo.UserFields.UPDATED_AT: datetime.datetime.now()
            }
            
            query, params = database.BaseQueries.update(
                database.TableNames.USERS,
                user_update,
                {userinfo.UserFields.USER_ID: user_id}
            )
            self.db.execute(query, params)
            
            return {
                "success": True,
                "user_id": user_id,
                "plan": plan.value,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "message": "Подписка успешно активирована"
            }
            
        except Exception as e:
            return {
                "success": False, 
                "error": str(e),
                "message": "Ошибка активации подписки"
            }

    def process_refund(self, user_id: int, payment_charge_id: str) -> typing.Dict[str, typing.Any]:
        """
        Обрабатывает возврат средств через метод refundStarPayment[citation:1].
        """
        try:
            success = self.bot.refund_star_payment(user_id, payment_charge_id)
            
            if success:
                # Обновляем статус платежа в БД
                update_data = {
                    "status": PaymentStatus.REFUNDED.value,
                    "refunded_at": datetime.datetime.now()
                }
                
                query, params = database.BaseQueries.update(
                    database.TableNames.PAYMENTS,
                    update_data,
                    {"telegram_payment_charge_id": payment_charge_id}
                )
                self.db.execute(query, params)
                
                # Деактивируем подписку пользователя
                user_update = {
                    userinfo.UserFields.IS_PREMIUM: False,
                    userinfo.UserFields.STATUS: "free",
                    userinfo.UserFields.UPDATED_AT: datetime.datetime.now()
                }
                
                query, params = database.BaseQueries.update(
                    database.TableNames.USERS,
                    user_update,
                    {userinfo.UserFields.USER_ID: user_id}
                )
                self.db.execute(query, params)
            
            return {
                "success": success,
                "message": "Возврат выполнен успешно" if success else "Ошибка возврата"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка обработки возврата"
            }

    def _get_plan_description(self, plan: database.SubscriptionPlan) -> str:
        """Возвращает описание плана подписки."""
        descriptions = {
            database.SubscriptionPlan.BASIC: "Базовый план: доступ к основным функциям создания коллажей",
            database.SubscriptionPlan.PREMIUM: "Премиум план: расширенные возможности и приоритетная обработка", 
            database.SubscriptionPlan.PRO: "PRO план: полный доступ ко всем функциям без ограничений"
        }
        return descriptions.get(plan, "Подписка на сервис коллажей")
    
    def _get_plan_info(self, plan: database.SubscriptionPlan) -> str:
        """Возвращает описание плана подписки."""
        titles = {
            database.SubscriptionPlan.BASIC: f"Подписка: уровень {database.SubscriptionPlan.BASIC.value.upper()}",
            database.SubscriptionPlan.PREMIUM: f"Подписка: уровень {database.SubscriptionPlan.BASIC.value.upper()}",
            database.SubscriptionPlan.PRO: f"Подписка: уровень {database.SubscriptionPlan.BASIC.value.upper()}",
        }
        descriptions = {
            database.SubscriptionPlan.BASIC: "Базовый план: доступ к основным функциям создания коллажей",
            database.SubscriptionPlan.PREMIUM: "Премиум план: расширенные возможности и приоритетная обработка", 
            database.SubscriptionPlan.PRO: "PRO план: полный доступ ко всем функциям без ограничений"
        }
        title = titles.get(plan, "Подписка на сервис коллажей")
        description = descriptions.get(plan, "Подписка на сервис коллажей")
        return title, description

    def __str__(self):
        if self.db:
            return f"PaymentManager(db: {self.db})"
        return "PaymentManager(empty)"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Возвращает представление объекта в виде словаря.

        Возвращает:
            dict: словарь с информацией об изображении
        """
        return {
            "PaymentManager": self.__str__()
        }

    # Методы check_subscription_status, get_user_payments и др. остаются без изменений
    # из предыдущей реализации, так как они работают с вашей внутренней БД

if __name__ == "__main__":
    dotenv.load_dotenv("dev.env")
    BOT_API_KEY = os.getenv("BOT_API_KEY")

    bot = telebot.TeleBot(BOT_API_KEY)

    bot.send_invoice()