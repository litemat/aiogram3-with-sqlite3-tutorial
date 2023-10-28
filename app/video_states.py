# Импортируем все необходимое для машины состояний ( FSM )
from aiogram.fsm.state import StatesGroup, State

"""

    Создаем "шаги" для определенного действия.
    
                        -- --
                        
    В данном случае для добавления видео и его описания.


"""


# Класс обязательно должен наследоваться от StatesGroup ( смотреть на [2] строке в from aiogram.fsm.state import )
class StepsVideoAdd(StatesGroup):
    # Создаем шаг добавления видео
    GET_VIDEO = State()

    # Создаем шаг для добавления описания видео
    GET_VIDEO_DESCRIPTION = State()
