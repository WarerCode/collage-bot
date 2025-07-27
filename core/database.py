import random
import re
import sqlite3
from dotenv import load_dotenv
import os
from logs.logger import logger


load_dotenv('config.env')
DB_NAME = os.getenv('DB_NAME')


# Инициализация БД
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL UNIQUE,
        popularity INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_images (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        user_id INTEGER NOT NULL,
        file_id TEXT UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_tags (
        image_id BIGINT NOT NULL,
        tag_id BIGINT NOT NULL,
        PRIMARY KEY (image_id, tag_id),
        CONSTRAINT image_id_fk FOREIGN KEY (image_id) REFERENCES user_images (id) ON DELETE CASCADE,
        CONSTRAINT tag_id_fk FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_group_tags (
        image_group_id BIGINT NOT NULL,
        tag_id BIGINT NOT NULL,
        PRIMARY KEY (image_group_id, tag_id),
        CONSTRAINT tag_id_fk FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

    logger.debug(f"database: {DB_NAME} was initialized")

# Сохранение информации о изображении
def save_image_to_database(user_id: int, file_id: str, group_id: int=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_images (user_id, group_id, file_id) VALUES (?, ?, ?)",
        (user_id, group_id, file_id)
    )
    conn.commit()
    conn.close()

# Сохранение информации о теге
def save_tag_to_database(name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tags (name) VALUES (?)",
        (name,)
    )
    conn.commit()
    conn.close()

# Сохранение информации о связи тега и изображения
def save_image_tag_to_database(image_id: int, tag_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)",
        (image_id, tag_id)
    )
    conn.commit()
    conn.close()

# Сохранение информации о связи тега и группы изображений
def save_image_tag_to_database(image_group_id: int, tag_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO image_group_tags (image_group_id, tag_id) VALUES (?, ?)",
        (image_group_id, tag_id)
    )
    conn.commit()
    conn.close()

# Сохранение полной информации о изображении и связных с ним тегов
# (Использовать в load_image)
def save_to_database(user_id: int, file_id: str, tag_names: list[str]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO user_images (user_id, file_id) VALUES (?, ?)",
            (user_id, file_id)
        )
        
        cursor.execute("SELECT id FROM user_images WHERE file_id = ?", (file_id,))
        image_id = cursor.fetchone()[0]
        
        for tag_name in tag_names:
            cursor.execute(
                "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                (tag_name,)
            )
            
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)",
                (image_id, tag_id)
            )
        
        conn.commit()
        logger.info("database.save_to_database:: success")
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"database.save_to_database:: saving im db was wrong: {e}")
        return False

    finally:
        conn.close()

# Сохранение полной информации о изображении и связных с ним тегов
# (Использовать в load_image)
def bulk_save_to_database(user_id: int, file_ids: list[str], image_group_id: int, tag_names: list[str]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        for file_id in file_ids:
            cursor.execute(
                "INSERT OR IGNORE INTO user_images (user_id, group_id, file_id) VALUES (?, ?, ?)",
                (user_id, image_group_id, file_id)
            )
            
        for tag_name in tag_names:
            cursor.execute(
                "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                (tag_name,)
            )
            
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT OR IGNORE INTO image_group_tags (image_group_id, tag_id) VALUES (?, ?)",
                (image_group_id, tag_id)
            )
            
            conn.commit()
            logger.info("database.bulk_save_to_database:: success")
            return True

    except Exception as e:
        conn.rollback()
        logger.error(f"database.bulk_save_to_database::failed to save in db: {e}")
        return False

    finally:
        conn.close()

# Получение списка айди изображений по списку тегов
def get_images_by_tags(tag_names: list[str]) -> list[str]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        result = []
        placeholders = ",".join(["?"] * len(tag_names))
        
        cursor.execute(f"""
            SELECT DISTINCT user_images.file_id FROM user_images
            JOIN image_tags ON user_images.id = image_tags.image_id
            JOIN tags ON image_tags.tag_id = tags.id
            WHERE tags.name IN ({placeholders})
        """, tag_names)

        result += cursor.fetchall()

        cursor.execute(f"""
            SELECT DISTINCT user_images.file_id FROM user_images
            JOIN image_group_tags ON user_images.group_id = image_group_tags.image_group_id
            JOIN tags ON image_group_tags.tag_id = tags.id
            WHERE tags.name IN ({placeholders})
        """, tag_names)

        result += cursor.fetchall()

        # cursor.execute(f"""
        #    SELECT DISTINCT user_images.file_id FROM user_images
        #    JOIN image_tags ON user_images.id = image_tags.image_id
        #    JOIN tags ON image_tags.tag_id = tags.id
        #    JOIN image_group_tags ON user_images.group_id = image_group_tags.image_group_id
        #    JOIN tags ON image_group_tags.tag_id = tags.id
        #    WHERE tags.name IN ({placeholders})
        # """, tag_names)

        # result += cursor.fetchall()

        file_ids = [row[0] for row in set(result)]
        return file_ids

    except Exception as e:
        logger.error(f"database.get_images_by_tags::failed to find files id: {e}")
        return []

    finally:
        conn.close()

# Увеличение популярности для списка тегов
def increment_tag_popularity(tag_names: list[str]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            "UPDATE tags SET popularity = popularity + 1 WHERE name = ?",
            [(name,) for name in tag_names]
        )
        conn.commit()
        return True

    except Exception as e:
        logger.error(f"database.increment_tag_popularity:: failed to update tags popularity: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

# Получение N наиболее популярных тегов (список названий)
def get_most_popular_tags(n: int=4):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT name FROM tags 
            ORDER BY popularity DESC
            LIMIT ?
        """, (n,))
        conn.commit()
        result = cursor.fetchall()
        return [row[0] for row in result]

    except Exception as e:
        logger.error(f"database.get_most_popular_tags::failed to choose {n} most popular tags: {e}")
        conn.rollback()
        return []

    finally:
        conn.close()

# Получение тегов с такими же первыми буквами (список названий)
def get_start_tags(tags: list[str]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    first_symbols = tuple(set([tag[0] for tag in tags]))
    question_str = ",".join(['?' for _ in range(len(first_symbols))])

    try:
        cursor.execute(f"""
            SELECT name FROM tags 
            WHERE SUBSTR(name, 1, 1) IN ({question_str})
        """, first_symbols)
        conn.commit()
        result = cursor.fetchall()
        return [row[0] for row in result]

    except Exception as e:
        logger.error(f"database.get_start_tags:: failed to choose near meaning tags: {e}")
        conn.rollback()
        return []

    finally:
        conn.close()
