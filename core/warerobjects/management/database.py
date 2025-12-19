"""
@JaneeWaterlemonka допиши красивый полный комментарий
"""

import os
import sqlite3
import psycopg2
import psycopg2.extras as ps_extras
import enum
import contextlib
import dotenv
import abc

import core.warerobjects.warerobject as warer
import core.warerobjects.data.userinfo as userinfo

class DBTypes(enum.Enum):
    """
    Допустимые типы базы данных
    """
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"

class TableNames(enum.Enum):
    """
    Список названий таблиц базы данных
    """
    USERS= "users"
    IMAGES= "images"
    TAGS= "tags"
    IMAGE_TAG_RELATIONS= "image_tag_relations"
    PAYMENTS= "payments"
    # По умолчанию поле price для всех таблиц *_PLANS указывается в валюте XTR
    # SUBSCRIPTION_PLANS= "subscription_plans"
    SUBSCRIPTIONS= "subscriptions"

    def __str__(self):
        return self.value
    
class ProductTableNames(enum.Enum):
    """
    Список названий таблиц базы данных
    
    """
    SUBSCRIPTIONS= TableNames.SUBSCRIPTIONS.value

    def __str__(self):
        return self.value
    
class SubscriptionPlan(enum.Enum):
    """Планы подписок"""
    BASIC = "basic"
    PREMIUM = "premium" 
    PRO = "pro"

class TableConfig(abc.ABC):
    """Конфигурация таблиц с информацией о первичных ключах"""
    
    TABLE_PRIMARY_KEYS = {
        TableNames.USERS: userinfo.UserFields.USER_ID,
        TableNames.IMAGES: "id",
        TableNames.TAGS: "id",
        TableNames.IMAGE_TAG_RELATIONS: ("image_id", "tag_id"),
        TableNames.PAYMENTS: "id",
        # TableNames.SUBSCRIPTION_PLANS: "id",
        TableNames.SUBSCRIPTIONS: "id",
    }
    
    @classmethod
    def get_primary_key(cls, table_name: TableNames):
        """
        Получение первичного ключа таблицы.

        Аргументы:
            table_name (TableNames): имя таблицы

        Возвращает:
            str: если первичный ключ простой
            tuple: если первичный ключ составной
        """
        return cls.TABLE_PRIMARY_KEYS.get(table_name)

class TableQueries(enum.Enum):
    """
    Набор запросов в базу данных
    """
    CREATE_TABLE_USERS = f"""
        CREATE TABLE IF NOT EXISTS {TableNames.USERS.value} (
            {userinfo.UserFields.USER_ID} INTEGER PRIMARY KEY,
            {userinfo.UserFields.USERNAME} VARCHAR(100),
            {userinfo.UserFields.IS_BOT} BOOLEAN DEFAULT FALSE,
            {userinfo.UserFields.STATUS} VARCHAR(100),
            {userinfo.UserFields.FIRST_NAME} VARCHAR(100),
            {userinfo.UserFields.LAST_NAME} VARCHAR(100),
            {userinfo.UserFields.LANGUAGE_CODE} VARCHAR(10),
            {userinfo.UserFields.IS_PREMIUM} BOOLEAN DEFAULT FALSE,
            {userinfo.UserFields.FREE_COLLAGES_REMAINING} INTEGER DEFAULT %s,
            {userinfo.UserFields.LAST_COLLAGE_DATE} DATE,
            {userinfo.UserFields.UPDATED_AT} TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            {userinfo.UserFields.CREATED_AT} TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    CREATE_TABLE_IMAGES = f"""
       CREATE TABLE IF NOT EXISTS {TableNames.IMAGES.value} (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            file_id TEXT UNIQUE NOT NULL,
            times_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {TableNames.USERS.value}(user_id) ON DELETE CASCADE
        );
    """
    CREATE_TABLE_TAGS = f"""
       CREATE TABLE IF NOT EXISTS {TableNames.TAGS.value} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(30) UNIQUE,
            times_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        );
    """
    CREATE_TABLE_IMAGE_TAG_RELATIONS = f"""
       CREATE TABLE IF NOT EXISTS {TableNames.IMAGE_TAG_RELATIONS.value} (
            image_id INTEGER,
            tag_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (image_id, tag_id),
            FOREIGN KEY (image_id) REFERENCES {TableNames.IMAGES.value}(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES {TableNames.TAGS.value}(id) ON DELETE CASCADE
        );
    """
    CREATE_TABLE_PAYMENTS = f"""
        CREATE TABLE IF NOT EXISTS {TableNames.PAYMENTS.value} (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            item_type VARCHAR(50) NOT NULL CHECK (item_type IN ({", ".join(product.value for product in ProductTableNames)})),
            telegram_payment_charge_id VARCHAR(200) DEFAULT '',
            amount DECIMAL(10, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'STR',
            method VARCHAR(50), -- 'yookassa', 'crypto', и т.д.
            status VARCHAR(50), -- 'pending', 'completed', и т.д.
            data JSON, -- данные о платеже
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {TableNames.USERS.value}(user_id) ON DELETE CASCADE
        );
    """
    # CREATE_TABLE_SUBSCRIPTION_PLANS = f"""
    #     CREATE TABLE IF NOT EXISTS {TableNames.SUBSCRIPTION_PLANS.value} (
    #         id SERIAL PRIMARY KEY,
    #         type VARCHAR(50) UNIQUE NOT NULL CHECK (type IN ({", ".join(plan.value for plan in SubscriptionPlan)})),
    #         name VARCHAR(100) NOT NULL,
    #         description TEXT,
    #         price DECIMAL(10, 2) NOT NULL,
    #         duration INTERVAL NOT NULL,
    #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #         FOREIGN KEY (payment_id) REFERENCES {TableNames.PAYMENTS.value}(id) ON DELETE SET NULL
    #     );
    # """
    CREATE_TABLE_SUBSCRIPTIONS = f"""
        CREATE TABLE IF NOT EXISTS {TableNames.SUBSCRIPTIONS.value} (
            id SERIAL PRIMARY KEY,
            plan_type VARCHAR(50) NOT NULL,
            user_id INTEGER NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {TableNames.USERS.value}(id) ON DELETE CASCADE
        );
    """

class BaseQueries(abc.ABC):
    """
    Набор запросов в базу данных для пользователя
    """
    @classmethod
    def makeCondition(cls, data: dict, separator: str="AND") -> str:
        """
        Формирование строки для передачи в условие WHERE, HAVING.

        Аргументы:
            data (dict): данные для формирования условия
            separator (str): разделитель

        Возвращает:
            str: строка условия
        """
        res_condition = []
        for key, val in data.items():
            res_condition.append(f"{key} = '{val}'")
        res_condition = f" {separator} ".join(res_condition)
        return res_condition
    
    @classmethod
    def makePlaceholders(cls, length: int) -> str:
        """
        Формирование строки из заполнителей, для дальнейшего ваполнения параметрами.

        Аргументы:
            length (int): количество заполнителей

        Возвращает:
            str: строка заполнителей
        """
        return ", ".join(["%s"] * length)

    @classmethod
    def insert(cls,
               table_name: TableNames,
               data: dict) -> tuple[str, list]:
        """
        Добавление в таблицу записи.

        Аргументы:
            table_name (TableNames): имя таблицы
            data (dict): данные объекта

        Возвращает:
            str: запрос на вставку
            list: список параметров
        """
        keys = ", ".join(data.keys())
        pk = TableConfig.get_primary_key(table_name)

        if isinstance(pk, list):
            # Для составных ключей нужен особый подход
            conflict_clause = ', '.join(pk)
        else:
            conflict_clause = pk

        query = f"""
            INSERT INTO
            {table_name} ({keys})
            VALUES ({cls.makePlaceholders(len(data))})
            ON CONFLICT ({conflict_clause}) DO NOTHING;
        """
        return query, list(data.values())
    
    @classmethod
    def select(cls,
               table_name: TableNames,
               columns: list="*",
               conditions: dict=None) -> tuple[str, list]:
        """
        Получение данных из таблицы.

        Аргументы:
            table_name (TableNames): имя таблицы
            columns (list): колонки для получения
            conditions (dict): условия фильтрации выборки

        Возвращает:
            str: запрос на получение
            list: список параметров
        """
        columns = ", ".join(columns)
        params = []
        if conditions:
            query = f"""
                SELECT {columns} FROM {table_name} WHERE {cls.makeCondition(conditions)};
            """
        else:
            query = f"""
                SELECT {columns} FROM {table_name};
            """

        return query, params
    
    @classmethod
    def update(cls,
               table_name: TableNames,
               data: dict,
               conditions: dict=None) -> tuple[str, list]:
        """
        Обновление записей в таблице.

        Аргументы:
            table_name (TableNames): имя таблицы
            data (dict): данные объекта
            conditions (dict): условия фильтрации выборки

        Возвращает:
            str: запрос на обновление
            list: список параметров
        """
        params = []
        if conditions:
            query = f"""
                UPDATE {table_name} SET {cls.makeCondition(data, ",")} WHERE {cls.makeCondition(conditions)};
            """
        else:
            query = f"""
                UPDATE {table_name} SET {cls.makeCondition(data, ",")};
            """
        return query, params
    
    @classmethod
    def delete(cls,
               table_name: TableNames,
               conditions: dict=None) -> tuple[str, list]:
        """
        Удаление записей из таблицы.

        Аргументы:
            table_name (TableNames): имя таблицы
            conditions (dict): условия фильтрации выборки

        Возвращает:
            str: запрос на удаление
            list: список параметров
        """
        params = []
        if conditions:
            query = f"""
                DELETE FROM {table_name} WHERE {cls.makeCondition(conditions)};
            """
        else:
            query = f"""
                DELETE FROM {table_name};
            """
        return query, params
    

class Database(warer.WarerObject):
    def __init__(self, db_type=DBTypes.POSTGRESQL, **kwargs):
        super().__init__()
        self.db_type = db_type
        self.connection_params = kwargs
        print(self.connection_params)

        queries_list = [
            (TableQueries.CREATE_TABLE_USERS.value, (3,)),
            (TableQueries.CREATE_TABLE_TAGS.value, None),
            (TableQueries.CREATE_TABLE_IMAGES.value, None),
            (TableQueries.CREATE_TABLE_IMAGE_TAG_RELATIONS.value, None),
            (TableQueries.CREATE_TABLE_PAYMENTS.value, None),
            (TableQueries.CREATE_TABLE_SUBSCRIPTION_PLANS.value, None),
        ]

        self.execute_many(queries_list)
    
    @contextlib.contextmanager
    def get_connection(self):
        """
        Получение соединения к базе данных

        Пример:
            >>> with self.get_connection() as conn:
                    conn.execute(...)
        """
        if self.db_type == DBTypes.SQLITE:
            conn = sqlite3.connect(self.connection_params['database'])
            conn.row_factory = sqlite3.Row
        elif self.db_type == DBTypes.POSTGRESQL:
            conn = psycopg2.connect(**self.connection_params)
        else:
            raise ValueError("Unsupported database type")
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute(self, query: str, params: list=None):
        """
        Отправка 1 запроса в базу данных.

        Аргументы:
            query (str): запрос (составлен BaseQueries, TableQueries или вручную)
            params (list): параметры для заполнения

        Возвращает:
            Cursor: курсор базы данных
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=ps_extras.RealDictCursor)
            cursor.execute(query, params or [])
            return cursor
        
    def execute_many(self, data: list):
        """
        Отправка нескольких запросов в базу данных.

        Аргументы:
            data (list): список кортежей вида:
                (query (str): запрос, params (list): параметры для заполнения)
        Возвращает:
            Cursor: курсор базы данных
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=ps_extras.RealDictCursor)
            for query, params in data:
                cursor.execute(query, params or [])
            return cursor
    
    def fetch_one(self, query, params=None):
        """
        Получение первой записи из выполненного запроса.

        Аргументы:
            query (str): запрос (составлен BaseQueries, TableQueries или вручную)
            params (list): параметры для заполнения
        Возвращает:
            RealDictRow: словарь (атрибут: значение) полученной записи
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=ps_extras.RealDictCursor)
            cursor.execute(query, params or [])
            return cursor.fetchone()
    
    def fetch_all(self, query, params=None):
        """
        Получение первой записи из выполненного запроса.

        Аргументы:
            query (str): запрос (составлен BaseQueries, TableQueries или вручную)
            params (list): параметры для заполнения
        Возвращает:
            list[RealDictRow]: список словарей (атрибут: значение) полученных записей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=ps_extras.RealDictCursor)
            cursor.execute(query, params or [])
            return cursor.fetchall()
        
    def __str__(self):
        return f"Database(db_type={self.db_type}, connection_params={self.connection_params})"

    def __repr__(self):
        return f"Database(db_type={self.db_type}, connection_params={self.connection_params})"

    def to_dict(self):
        return {
            "db_type": self.db_type,
            "connection_params": self.connection_params,
        }

if __name__ == "__main__":
    dotenv.load_dotenv("dev.env")
    
    print("Пример использования базы данных:")
    print()

    db = Database(DBTypes.POSTGRESQL,
              host=os.getenv("DB_HOST"), 
              database=os.getenv("DB_NAME"),
              user=os.getenv("DB_USER"),
              password=os.getenv("DB_PASSWORD"))
    
    # Очистка перед тестированием
    q, p = BaseQueries.delete(TableNames.TAGS)
    db.execute(q, p)

    q, p = BaseQueries.insert(TableNames.TAGS, {"name": "harry_potter", "times_used": 1})
    db.execute(q, p)

    q, p = BaseQueries.select(TableNames.TAGS, conditions={"name": "harry_potter", "times_used": 1})
    temp_tag = db.fetch_one(q, p)
    print(f"Полученный тег: {temp_tag}")

    q, p = BaseQueries.update(TableNames.TAGS, {"name": "germiona", "times_used": 5}, conditions={"id": temp_tag.get("id")})
    db.execute(q, p)
    q, p = BaseQueries.select(TableNames.TAGS, conditions={"name": "germiona", "times_used": 5})
    temp_tag = db.fetch_one(q, p)
    print(f"Тег после изменения: {temp_tag}")

    q, p = BaseQueries.delete(TableNames.TAGS, conditions={"id": temp_tag.get("id")})
    db.execute(q, p)
    print(f"Тег с именем {temp_tag.get('name')} был удалён")

    q, p = BaseQueries.select(TableNames.TAGS, conditions={"name": "harry_potter", "times_used": 1})
    temp_tags = db.fetch_all(q, p)
    print(f"Список тегов, после удаления: {temp_tags}")
    print()
    

    print(db.__str__())
    print(db.__repr__())
    print(db.to_dict())

    print()