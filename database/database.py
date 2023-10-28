import sqlite3

# Создание базы данных с названием "test"
db = sqlite3.connect('test.db')
# Создание курсора (  db.cursor()   )     ->     (sqlite3.connect('test.db').cursor()  )
cur = db.cursor()

# Создание таблицы "videos" в Базе данных "test.db"
async def create_table_videos():
    cur.execute("""CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id VARCHAR(500),
        video_description VARCHAR(255) 
    )""")

    # Сохраняем изменения в базе данных - - - - - -
    db.commit()
    # - - - - - - - - - - - - - - - - - - - - - - -