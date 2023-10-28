from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# deffault main keyboards = = = = == = = = = == = = = = == = = = =

# Кнопки если видосов вообще нет
cmd_start_if_videos_empty_kb = [
    [InlineKeyboardButton(text='Загрузить видео', callback_data='video_add')]
]

cmd_start_if_videos_empty = InlineKeyboardMarkup(inline_keyboard=cmd_start_if_videos_empty_kb)


# Кнопки если видосы есть
cmd_start_if_videos_kb = [
    [InlineKeyboardButton(text='Загрузить видео', callback_data='video_add'),
     InlineKeyboardButton(text='Посмотреть видео', callback_data='video_view')]
]

cmd_start_if_videos = InlineKeyboardMarkup(inline_keyboard=cmd_start_if_videos_kb)


# Кнопки для проверки ( правильно / неправильно ) введеных данных для добавления видео
cmd_video_add_check_kb = [
    # Если [ Заново ] то просто по новой запускаем шаги машины состояний ( FSM ) -> ( смотреть на [14 - 15] строках )
    [InlineKeyboardButton(text='Заново', callback_data='video_add'),

     # Если [ Верно ] создаем новый [ callback_data ] -> который будем обрабатывать в app/handlers.py
     InlineKeyboardButton(text='Верно', callback_data='video_add_accept')]
]

cmd_video_add_check = InlineKeyboardMarkup(inline_keyboard=cmd_video_add_check_kb)


# = = = = == = = = = == = = = = == = = = = == = = = = == = = = = ==