import sqlite3
import psycopg2
import enum
from contextlib import contextmanager

import core.warerobjects.warerobject as warer

class DBTypes(enum.Enum):
    """
    Допустимые типы базы данных
    """
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class Queries(enum.Enum):
    """
    Набор запросов в базу данных
    """
    CREATE_TABLE_USERS = """
        CREATE TABLE IF NOT EXISTS users (
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        );
    """
    CREATE_TABLE_IMAGES = """
       CREATE TABLE images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_id TEXT UNIQUE NOT NULL,
            times_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        );
    """
    CREATE_TABLE_TAGS = """
       CREATE TABLE tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(30) UNIQUE,
            times_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        );
    """
    CREATE_TABLE_IMAGE_TAG_RELATIONS = """
       CREATE TABLE image_tag_relations (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
        );
    """
    CREATE_TABLE_PAYMENTS = """
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'STR',
            method VARCHAR(50), -- 'yookassa', 'crypto', и т.д.
            data JSON, -- данные о платеже
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """
    CREATE_TABLE_SUBSCRIPTION_PLANS = """
        CREATE TABLE subscription_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE SET_NULL
        );
    """
    

class Database(warer.WarerObject):
    def __init__(self, db_type=DBTypes.SQLITE, **kwargs):
        super().__init__()
        self.db_type = db_type
        self.connection_params = kwargs
    
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
    print("пример использования политик:")
    help(Database)
    print()

    db = Database(DBTypes.SQLITE, database='bot.db')
    print(db.__str__())

    db = Database('postgresql', 
              host='localhost', 
              database='bot_db',
              user='user',
              password='pass')
    print(db.__str__())

    print()