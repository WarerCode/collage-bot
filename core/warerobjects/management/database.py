import os
import sqlite3
import psycopg2
import enum
from contextlib import contextmanager
from dotenv import load_dotenv
import abc

load_dotenv("config.env")


import core.warerobjects.warerobject as warer

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
    SUBSCRIPTION_PLANS= "subscription_plans"

class Queries(enum.Enum):
    """
    Набор запросов в базу данных
    """
    CREATE_TABLE_USERS = f"""
        CREATE TABLE IF NOT EXISTS {TableNames.USERS} (
            user_id INTEGER PRIMARY KEY,
            username VARCHAR(100),
            is_bot BOOLEAN DEFAULT FALSE,
            status VARCHAR(100),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            language_code VARCHAR(10),
            is_premium BOOLEAN DEFAULT FALSE,
            free_collages_remaining INTEGER DEFAULT %s,
            last_collage_date DATE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    CREATE_TABLE_IMAGES = f"""
       CREATE TABLE IF NOT EXISTS {TableNames.IMAGES} (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            file_id TEXT UNIQUE NOT NULL,
            times_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """
    CREATE_TABLE_TAGS = f"""
       CREATE TABLE IF NOT EXISTS {TableNames.TAGS} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(30) UNIQUE,
            times_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    CREATE_TABLE_IMAGE_TAG_RELATIONS = f"""
       CREATE TABLE IF NOT EXISTS {TableNames.IMAGE_TAG_RELATIONS} (
            image_id INTEGER,
            tag_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (image_id, tag_id),
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );
    """
    CREATE_TABLE_PAYMENTS = f"""
        CREATE TABLE IF NOT EXISTS {TableNames.PAYMENTS} (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'STR',
            method VARCHAR(50), -- 'yookassa', 'crypto', и т.д.
            data JSON, -- данные о платеже
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """
    CREATE_TABLE_SUBSCRIPTION_PLANS = f"""
        CREATE TABLE IF NOT EXISTS {TableNames.SUBSCRIPTION_PLANS} (
            id SERIAL PRIMARY KEY,
            payment_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE SET NULL
        );
    """

class BaseQueries(abc.ABC):
    """
    Набор запросов в базу данных для пользователя
    """
    @staticmethod
    def makeCondition(cls, data: dict):
        res_condition = []
        for key, val in data.items():
            res_condition.append(f"{key} = {val}")
        res_condition = ", ".join(res_condition)
        return res_condition

    @staticmethod
    def insert(cls, table_name: TableNames, data: dict):
        keys = ", ".join(data.keys())
        values = ", ".join(data.values())
        query = f"""
            INSERT INTO 
            {table_name} ({keys})
            VALUES ({values});
        """
        return query
    
    @staticmethod
    def select(cls, table_name: TableNames, columns: list, conditions: dict=None):
        columns = ", ".join(columns)
        if conditions:
            res_condition = cls.makeCondition(conditions)

            query = f"""
                SELECT {columns} FROM {table_name} WHERE {res_condition};
            """
        else:
            query = f"""
                SELECT {columns} FROM {table_name};
            """

        return query
    
    @staticmethod
    def update(cls, table_name: TableNames, data: dict, conditions: dict=None):
        items_str = cls.makeCondition(data)
        if conditions:
            res_condition = cls.makeCondition(conditions)
            query = f"""
                UPDATE {TableNames.USERS} SET {items_str} WHERE {res_condition};
            """
        else:
            query = f"""
                UPDATE {TableNames.USERS} SET {items_str};
            """
        return query
    
    @staticmethod
    def delete(cls, table_name: TableNames, conditions: dict):
        res_condition = cls.makeCondition(conditions)
        query = f"""
            DELETE FROM {table_name} WHERE {res_condition};
        """
        return query
    

class Database(warer.WarerObject):
    def __init__(self, db_type=DBTypes.POSTGRESQL, **kwargs):
        super().__init__()
        self.db_type = db_type
        self.connection_params = kwargs

        queries_list = [
            (Queries.CREATE_TABLE_USERS.value, (3,)),
            (Queries.CREATE_TABLE_TAGS.value, None),
            (Queries.CREATE_TABLE_IMAGES.value, None),
            (Queries.CREATE_TABLE_IMAGE_TAG_RELATIONS.value, None),
            (Queries.CREATE_TABLE_PAYMENTS.value, None),
            (Queries.CREATE_TABLE_SUBSCRIPTION_PLANS.value, None),
        ]

        self.execute_many(queries_list)
    
    @contextmanager
    def get_connection(self):
        """
        Получение соединения к базе данных

        Использовать конструкцию 
            < with self.get_connection() as conn: >
            чтобы соединение закрылось по завершении
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
    
    def execute(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            return cursor
        
    def execute_many(self, queries_list: list,):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for query, params in queries_list:
                cursor.execute(query, params or [])
            return cursor
    
    def fetch_one(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            return cursor.fetchone()
    
    def fetch_all(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
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
    print("Пример использования базы данных:")
    # help(Database)
    print()

    # db = Database(DBTypes.POSTGRESQL, database='bot.db')
    # print(db.__str__())

    db = Database(DBTypes.POSTGRESQL, 
              host=os.getenv("DB_HOST"), 
              database=os.getenv("DB_NAME"),
              user=os.getenv("DB_USER"),
              password=os.getenv("DB_PASSWORD"))
    print(db.__str__())
    print(db.__repr__())
    print(db.to_dict())

    print()