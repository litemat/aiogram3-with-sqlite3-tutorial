from aiogram import Dispatcher, Bot, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject, CommandStart

# Импорт Bot API через config.py КАК [ cfg ]
import config.config as cfg

# Импорт базы данных для создания таблиц КАК [ db ]
import database.database as db

# Импорт шагов для машины состояний ( FSM )
from app.video_states import StepsVideoAdd

# Импорт кнопок ( клавиатуры ) из app/keyboards.py КАК [ kb ]
import app.keyboards as kb


# Инициализируем роутер
router = Router()
boot = Bot(token=cfg.TOKEN)


# Фича для удаления сообщений
# Ее я использовать не буду, для твоего удобства
async def delete_messages(chat_id, message_id):
    await boot.delete_message(chat_id=chat_id, message_id=message_id)
    await boot.delete_message(chat_id=chat_id, message_id=message_id - 1)


# Начинаем "слушать и узнавать"
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'{message.from_user.first_name}, привет :)')

    # Запускаем проверку в таблице "videos" -> сть ли вообще видосы?
    db.cur.execute("""SELECT * FROM videos""")
    row = db.cur.fetchone()

    # Если видосов нет то:
    if not row:
        await message.answer(f'Во мне нет видео, заполни меня сэмпай ;)',
                             reply_markup=kb.cmd_start_if_videos_empty)
    else:
        await message.answer(f'Во мне есть видео, ура! :)',
                             reply_markup=kb.cmd_start_if_videos)


# Теперь будем слушать нажатия на кнопки
@router.callback_query(F.data == 'video_add')
async def cmd_video_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отправьте мне видео', show_alert=True)
    await callback.message.answer(f'Отправляй свое видео')

    # Переходим на шаг добавления видео
    await state.set_state(StepsVideoAdd.GET_VIDEO)


# Ловим ( только ) переход на шаг добавления видео в машине состояний ( FSM )
@router.message(StepsVideoAdd.GET_VIDEO)
async def cmd_video_add_get_video(message: Message, state: FSMContext):
    # Обновляем данные в машине состояний ( FSM )
    # Сейчас это [id] видео
    # Так же сделаем проверку что отправил нам пользователь

    # Если он отправил нам НЕ видео
    if not message.video:
        # Обрываем шаги в машине состояний ( FSM )
        await state.clear()

        # Пишем что он ну дебил
        await message.answer(f'И первое место по идиотизму достаеться:\n'
                             f'{message.from_user.first_name}\n\n'
                             f'Нужно было отправить видео, а ты что отправил?!',
                             reply_markup=kb.cmd_start_if_videos)
    # Если он отправил видео
    else:
        # Записываем [id] видео
        await state.update_data(video_id=message.video.file_id)
        #Говорим что он молодец и что делать дальше
        await message.answer(f'Молодец {message.from_user.first_name}\n'
                             f'Теперь отправь описание видео')

        # Переходим на следующий шаг добавсления описания в машине состояний ( FSM )
        await state.set_state(StepsVideoAdd.GET_VIDEO_DESCRIPTION)


# Ловим ( только ) переход на шаг добавления описания видео в машине состояний ( FSM )
@router.message(StepsVideoAdd.GET_VIDEO_DESCRIPTION)
async def cmd_video_add_get_video_description(message: Message, state: FSMContext):
    # Тут уже плевать че он там отправит, поэтому просто записываем в машину состояний ( FSM ) его ответ
    await state.update_data(video_description=message.text)

    # Теперь получаем все рание записанные переменные в машине состояний ( FSM )
    context_data = await state.get_data()

    video_id = context_data.get('video_id')
    video_description = context_data.get('video_description')

    # Выведем все полученые данные на проверку, пользователю
    data = f'[id] Видео: {video_id}\n' \
           f'[Описание] Видео: {video_description}'

    await message.answer(f'{data}', reply_markup=kb.cmd_video_add_check)


# Теперь ловим [ callback_data ] на подтверждения добавления видео [ video_add_accept ]
# Тут уже не нужно ловить ШАГИ машины состояний -> так как мы еще не оборвали шаги машины состояний ( FSM )
@router.callback_query(F.data == 'video_add_accept')
async def cmd_video_add_video_add_accept(callback: CallbackQuery, state: FSMContext):
    # Снова получаем всю введеную ранее информацию в машине состояний ( FSM )
    context_data = await state.get_data()

    video_id = context_data.get('video_id')
    video_description = context_data.get('video_description')

    """
    
        Сейчас будем работать с базой данных -> с таблицей " videos "
        Внесем в нее всю информацию
    
    """
    # Обращаемся к таблице " videos " и вносим в нее значения при помощи [2] двух [ переменных ]

    # Подготавливаем запрос { insert } на [ запись в строки ( video_id и video_description ) в таблицу ( videos ) ]
    # Данных [ ( ?, ? ) -> которые мы внесем чуть ниже в { insert_data } ]
    insert = ("""INSERT INTO videos (video_id, video_description) VALUES (?, ?)""")
    # Собственно сами данные [ video_id и video_description ( смотреть на 112 - 113 ) строках ]
    insert_data = (video_id, video_description)

    # Производим манипуляцию с базой данных -> в частности с таблицей " videos "
    db.cur.execute(insert, insert_data)
    # После манипуляций с базой данных [ добавление / удаление / обновление ] данных не забываем сохранить изменения
    # [ db.db.commit() ]
    db.db.commit()

    # Для приличия ответим пользователю :)
    await callback.answer('Видео было добавленно', show_alert=True)
    await callback.message.answer(f'Вы успешно добавили видео', reply_markup=kb.cmd_start_if_videos)


    """
    
        Поздравляю мы заполнили таблицу " videos " одним элементом [ videos ] 
        с данными [ video_id и video_description ]
    
    """

    """
    
        КОГДА МЫ ВЫПОЛНИЛИ ВСЕ МАНИПУЛЯЦИИ С ПОМОЩЬЮ МАШИНЫ СОСТОЯНИЙ ( FSM ) И ЕЕ ДАННЫХ
        
        ВАЖНО!
        
        НЕ ЗАБЫВАЕМ СБРОСИТЬ ШАГИ МАШИНЫ СОСТОЯНИЙ ( FSM )
    
    """
    # обнуляем ( сбрасываем шаги машины состояний ( FSM ) )
    await state.clear()


"""

    Сейчас будем выводить все видео что есть в базе данных -> таблице " videos "

"""
# Обрабатываем ( ловим ) [ callback_data ] на показ всех видео
@router.callback_query(F.data == 'video_view')
async def cmd_video_view_all(callback: CallbackQuery):
    # Сейчас мы с помощью базы данных проверим есть ли вообще видео
    db.cur.execute("""SELECT video_id, video_description FROM videos""")
    rows = db.cur.fetchall()

    # Для начала отвечаем на [ callback_data ] чтобы избежать вида [ загрузки / прогрузки ] кнопки ( клавиатуры )
    # [ await callback.answer() ]
    await callback.answer()

    # если видео вообще НЕТ
    if not rows:
        # Пишем что видео нет и добавляем кнопки ( ЕСЛИ ВИДЕО НЕТ )
        await callback.message.answer(f'Во мне нет видео, заполни меня сэмпай ;)',
                                      reply_markup=kb.cmd_start_if_videos_empty)
    # если видосы есть ТО
    else:
        # Запускаем цикл который ( проверяет и выводит ) все видео с описаниями
        # Сейчас нам нет необходимости снова залезать в базу данных -> таблицу " videos "
        # Так как мы уже получили весь список видео оттуда ( смотреть на 165 - 166 ) строках
        await callback.message.answer(f'Ниже все добавленные видео что заполняют меня сэмпай ;)')
        for video_id, video_description in rows:
            await callback.message.answer_video(video=video_id, caption=video_description)

    """
    
        На этом сообственно всё, если что то не понятно смело задавай вопросы
        
        И кстати в данной манипуляции с базой данных -> таблицей " videos "
        нам НЕ нужно подтверждать изменения [ db.db.commit() ]
        
        Так как мы прочто читаем ( считываем ) и не привносим изменений [ добавление / удаление / обновление ]
        
        
        Надеюсь с этой документацией ты сможешь более менее разобраться в работе ;)
        
        
        
                                                                             DOCUMENTATION BY 
                                                                            
                                                                             Sarkissyan Artur and
                                                                                    SturtUp group 
                                                                            
                                                                             aiogram 3x & sqlite3
                                                                                       28.10.2023
    
    """















