import sqlite3

# Инициализация БД
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_images (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
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
    conn.commit()
    conn.close()

# Сохранение информации о изображении
def save_image_to_database(user_id: int, file_id: str):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_images (user_id, file_id) VALUES (?, ?)",
        (user_id, file_id)
    )
    conn.commit()
    conn.close()

def save_tag_to_database(name: str):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tags (name) VALUES (?)",
        (name,)
    )
    conn.commit()
    conn.close()

def save_image_tag_to_database(image_id: int, tag_id: int):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)",
        (image_id, tag_id)
    )
    conn.commit()
    conn.close()

def save_to_database(user_id: int, file_id: str, tag_names: list[str]):
    conn = sqlite3.connect("bot.db")
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
        print("Успех")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при сохранении в БД: {e}")
        return False
    finally:
        conn.close()
