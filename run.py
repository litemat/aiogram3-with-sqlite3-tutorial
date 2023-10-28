import asyncio

import aiogram.types
from aiogram import Dispatcher, Bot, types, F, Router

# Импорт базы данных для создания таблиц при включении
import database.database as db

# Импорт Bot API через config.py
import config.config as cfg

# Импортируем роутер из app/handlers.py
from app.handlers import router


# Программа и логика запуска бота:
async def init():
    bot = Bot(token=cfg.TOKEN)
    dp = Dispatcher()
    # Подключаем роутер из app/handlers.py
    dp.include_router(router)

    # Запускаем создание таблицы "videos" из database/database.py
    await db.create_table_videos()

    # Запускаем polling (отправку запросов в Телеграм)
    await dp.start_polling(bot)


# Сам запуск бота ( Исполняем программу и логику запуска из init() )
if __name__ == "__main__":
    try:
        asyncio.run(init())
        print("База данных успешно подключена")
    except TypeError as error:
        if error:
            print(f'Произошла ошибка (смотреть ниже)\n\n'
                  f'{error}')
        print('Отключение бота')
