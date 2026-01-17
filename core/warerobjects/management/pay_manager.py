"""
Менеджер платежей и подписок для Telegram бота.

Основные возможности:
- Создание счетов (инвойсов) через sendInvoice и createInvoiceLink.
- Обработка предварительных проверок (pre-checkout) и успешных платежей.
- Управление подписками.
- Возврат средств.
"""
import datetime
import json
import os
import typing
import enum
import telebot
import dotenv
import time
import psycopg2.extras as ps_extras

import core.warerobjects.warerobject as warer
import core.warerobjects.management.database as database

class PaymentType(enum.Enum):
    """Планы подписок  в системе."""
    SUBSCRIPTION = "subscription"

class PaymentStatus(enum.Enum):
    """Статусы платежей в системе."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentCurrency(enum.Enum):
    """Валюты платежей в системе."""
    STARS = "XTR"

class PaymentMethod(enum.Enum):
    """Методы оплаты в системе."""
    STARS = "stars"

class PaymentManager(warer.WarerObject):
    """
    Класс - менеджер платежей, реализующий логику в соответствии с Telegram Bot API.

    Атрибуты класса:
        SUBSCRIPTION_PRICES: Цены подписок в Telegram Stars (XTR)
        SUBSCRIPTION_DURATIONS: Длительности подписок в днях

    Атрибуты экземпляра:
        db: объект базы данных типа database.Database
        bot: объект телеграм бота типа telebot.TeleBot
    """
    
    SUBSCRIPTION_PRICES = {
        database.SubscriptionPlan.BASIC: 1,
        database.SubscriptionPlan.PREMIUM: 1,
        database.SubscriptionPlan.PRO: 1,
    }
    
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
            bot (telebot.TeleBot): объект телеграм бота
        """
        super().__init__()
        self.db = database
        self.bot = bot

    def create_subscription_invoice(
            self, 
            user_id: int, 
            plan: database.SubscriptionPlan, 
            chat_id: int = None
        ) -> typing.Dict[str, typing.Any]:
        """
        Создает инвойс для подписки через метод sendInvoice или createInvoiceLink.
        
        Аргументы:
            user_id (int): ID пользователя телеграм
            plan (database.SubscriptionPlan): выбранный план подписки
            chat_id (int): опционально, ID чата для отправки инвойса
            
        Возвращает:
            dict: результат создания инвойса
        """
        try:
            # Подготовка данных инвойса
            title, description = self._get_plan_info(plan)
            
            currency = PaymentCurrency.STARS.value
            amount = int(self.SUBSCRIPTION_PRICES[plan])
            
            # Цены
            prices = [
                telebot.types.LabeledPrice(
                    label=title,
                    amount=amount,
                )
            ]
            
            # provider_token - пустая строка для цифровых товаров
            provider_token = ""
            
            # Создаем запись о инвойсе в БД
            invoice_data = {
                "user_id": user_id,
                # "item_id": None,
                "item_type": database.ProductTableNames.SUBSCRIPTIONS.value,
                "amount": amount,
                "currency": currency,
                "method": PaymentMethod.STARS.value,
                "status": PaymentStatus.PENDING.value,
                "data": ps_extras.Json({
                    "plan": plan.value,
                }),
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
                    provider_token=provider_token,
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
        """
        Валидация данных pre-checkout запроса.
        
        Аргументы:
            query (telebot.types.PreCheckoutQuery): объект pre-checkout запроса
            
        Возвращает:
            dict: результат обработки данных платежа
        """
        try:
            # Проверяем возможность обработать заказ
            success = True

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

            checks = [
                plan is None,
                user_id != query.from_user.id,
                int(amount) != self.SUBSCRIPTION_PRICES[plan],
                PaymentCurrency(currency) is None,
                PaymentMethod(method) is None,
                PaymentStatus(status) is None,
            ]

            # print(checks)

            # print(plan)
            # print(user_id)
            # print(query.from_user.id)
            # print(int(amount))
            # print(self.SUBSCRIPTION_PRICES[plan])
            # print(PaymentCurrency(currency))
            # print(PaymentMethod(method))
            # print(PaymentStatus(status))

            # Проверка корректности данных
            if any(checks):
                success = False

            if success:
                return {
                    "success": True,
                    "method": "PreCheckoutQuery",
                    "result": checks,
                    "message": "Данные платежа успешно прошли валидацию"
                }
            else:
                return {
                    "success": False,
                    "method": "PreCheckoutQuery",
                    "result": checks,
                    "message": "Данные платежа не прошли валидацию"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": e,
                "message": "Ошибка при валидации данных платежа"
            }

    def handle_successful_payment(self, user_id: int, successful_payment: telebot.types.SuccessfulPayment) -> typing.Dict[str, typing.Any]:
        """
        Обрабатывает успешный платеж и активирует подписку.
        
        Аргументы:
            user_id (int): ID пользователя телеграм
            successful_payment (telebot.types.SuccessfulPayment): данные из поля successful_payment

        Возвращает:
            dict: результат обработки успешного платежа
        """
        try:
            # Извлекаем данные из платежа
            telegram_payment_charge_id = successful_payment.telegram_payment_charge_id

            invoice_payload = json.loads(successful_payment.invoice_payload)
            payment_id = invoice_payload.get("payment_id")
            
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
            payment = self.db.fetch_one(query, params)

            plan = database.SubscriptionPlan(payment.get("data", {}).get("plan"))

            if plan is None:
                raise ValueError("Некорректный план подписки")
            
            # Активируем подписку пользователя
            result = self._activate_subscription(user_id, plan)

            if result.get("item") and result.get("item")["id"]:
                update_data = {
                    "item_id": result.get("item")["id"],
                    "updated_at": datetime.datetime.now()
                }
                
                query, params = database.BaseQueries.update(
                    database.TableNames.PAYMENTS,
                    update_data,
                    {"id": payment_id, "user_id": user_id}
                )
                payment = self.db.fetch_one(query, params)

            return result

            
        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка обработки успешного платежа"
            }

    def _get_last_subscription(self, user_id: int, plan_type: str):
        subscription_select_query = f"""
            SELECT *
            FROM {database.TableNames.SUBSCRIPTIONS.value}
            WHERE user_id = %s
            AND plan_type = %s
            ORDER BY end_date DESC
            LIMIT 1;
        """
        subscription_select_params = [user_id, plan_type]

        subscription = self.db.fetch_one(subscription_select_query, subscription_select_params)
        return subscription

    def _activate_subscription(
            self, 
            user_id: int, 
            plan: database.SubscriptionPlan, 
        ) -> typing.Dict[str, typing.Any]:
        """
        Активирует подписку пользователя.
        
        Аргументы:
            user_id (int): ID пользователя телеграм
            plan (database.SubscriptionPlan): enum поле плана подписки

        Возвращает:
            dict: результат активации подписки
        """
        try:
            # Получаем последнию запись о платеже
            subscription = self._get_last_subscription(user_id, plan.value)

            now_time = datetime.datetime.now()
            duration_days = self.SUBSCRIPTION_DURATIONS[plan]

            # Проверяем если она существует и срок действия ещё не истёк
            if not (subscription is None or subscription.get("end_date") <= now_time):
                # Обновляем срок действия
                end_date = subscription.get("end_date") + datetime.timedelta(days=duration_days)
                subscription_query, subscription_params = database.BaseQueries.update(
                    database.TableNames.SUBSCRIPTIONS,
                    data={
                        "end_date": end_date,
                        "is_active": True,
                        "updated_at": now_time,
                    },
                    conditions={"id": subscription.get("id")}
                )
                subscription = self.db.fetch_one(subscription_query, subscription_params)
            else:
                # Создаём новую запись
                end_date = now_time + datetime.timedelta(days=duration_days)
                subscriptions_insert_query, subscriptions_insert_params = database.BaseQueries.insert(
                    database.TableNames.SUBSCRIPTIONS,
                    data={
                        "user_id": user_id, 
                        "plan_type": plan.value,
                        "start_date": now_time,
                        "is_active": True,
                        "end_date": end_date,
                    }
                )
                subscription = self.db.fetch_one(subscriptions_insert_query, subscriptions_insert_params)
            
            return {
                "success": True,
                "item": subscription,
                "user_id": user_id,
                "plan": plan.value,
                "end_date": end_date.__str__(),
                "message": "Подписка успешно активирована"
            }
            
        except Exception as e:
            print(e)
            return {
                "success": False, 
                "error": str(e),
                "message": "Ошибка активации подписки"
            }
        
    def _deactivate_subscription(
            self, 
            user_id: int, 
            item_id: int, 
        ) -> typing.Dict[str, typing.Any]:
        """
        Обновляет подписку пользователя после отмены платежа.
        
        Аргументы:
            user_id (int): ID пользователя телеграм
            item_id (int): ID подписки

        Возвращает:
            dict: результат обновления подписки
        """
        try:
            # Получаем подписку по item_id
            subscription_select_query, subscription_select_params = database.BaseQueries.select(
                table_name=database.TableNames.SUBSCRIPTIONS,
                conditions={"id": item_id}
            )

            subscription = self.db.fetch_one(subscription_select_query, subscription_select_params)

            if subscription is None:
                raise ValueError("Объект деактивации отсутствует")

            now_time = datetime.datetime.now()
            plan_value = subscription.get("plan_type")
            plan = database.SubscriptionPlan(plan_value)
            print(plan)
            if plan is None:
                raise ValueError("Поле plan отсутствует в data")
            duration_days = self.SUBSCRIPTION_DURATIONS[plan]
            print(duration_days)
            end_date = subscription.get("end_date") - datetime.timedelta(days=duration_days)
            print(end_date)

            # Обновляем срок действия подписки
            subscription_query, subscription_params = database.BaseQueries.update(
                database.TableNames.SUBSCRIPTIONS,
                data={
                    "end_date": end_date,
                    # "is_active": False,
                    "updated_at": now_time,
                },
                conditions={"id": item_id}
            )
            subscription = self.db.fetch_one(subscription_query, subscription_params)
            
            return {
                "success": True,
                "item": subscription,
                "user_id": user_id,
                "message": "Подписка успешно деактивирована"
            }
            
        except Exception as e:
            print(e)
            return {
                "success": False, 
                "error": str(e),
                "message": "Ошибка деактивации подписки"
            }

    def process_refund(self, user_id: int, payment_charge_id: str) -> typing.Dict[str, typing.Any]:
        """
        Обрабатывает возврат средств
        
        Аргументы:
            user_id (int): ID пользователя телеграм
            payment_charge_id (str): ID подписки

        Возвращает:
            dict: результат обновления подписки
        """
        try:
            success = self.bot.refund_star_payment(user_id, payment_charge_id)
            
            if success:
                # Обновляем статус платежа в БД
                update_data = {
                    "status": PaymentStatus.REFUNDED.value,
                    # "refunded_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now(),
                }
                
                query, params = database.BaseQueries.update(
                    database.TableNames.PAYMENTS,
                    update_data,
                    {"user_id": user_id, "telegram_payment_charge_id": payment_charge_id}
                )
                payment = self.db.fetch_one(query, params)
                
                # Деактивируем подписку пользователя
                deactivate_result = self._deactivate_subscription(user_id, payment.get("item_id"))

                print(deactivate_result.get("message"))
            
            return {
                "success": success,
                "message": "Возврат выполнен успешно" if success else "Ошибка возврата"
            }
            
        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка обработки возврата"
            }
        
    def check_subscription_info(self, user_id: int) -> typing.Dict[str, typing.Any]:
        """
        Обрабатывает возврат средств
        
        Аргументы:
            user_id (int): ID пользователя телеграм
            payment_charge_id (str): ID подписки

        Возвращает:
            dict: результат обновления подписки
        """
        try:
            sorted_subscription_plans = database.SubscriptionConfig.get_sorted_by_level()

            res_subscription = None

            if sorted_subscription_plans:
                for plan in sorted_subscription_plans[::-1]:
                    # Получаем последнию запись о платеже
                    subscription = self._get_last_subscription(user_id, plan.value)

                    now_time = datetime.datetime.now()

                    # Проверяем если она существует и срок действия ещё не истёк
                    if not (subscription is None or subscription.get("end_date") <= now_time):
                        res_subscription = subscription
                        break
                else:
                    res_subscription = None
            else:
                res_subscription = None
            
            return {
                "success": True,
                "item": res_subscription,
            }
            
        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка обработки возврата"
            }
    
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

if __name__ == "__main__":
    dotenv.load_dotenv("dev.env")
    BOT_API_KEY = os.getenv("BOT_API_KEY")

    bot = telebot.TeleBot(BOT_API_KEY)

    bot.send_invoice()