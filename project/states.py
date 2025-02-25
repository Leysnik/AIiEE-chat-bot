from aiogram.fsm.state import StatesGroup, State

class RegistrationForm(StatesGroup):
    """
    Класс, представляющий форму регистрации пользователя в боте
    
    Этот класс определяет состояния для регистрации пользователя, такие как:
        - name: имя пользователя
        - forename: фамилия пользователя
        - group: группа пользователя (например, учебная группа)
        - sex: пол пользователя

    Каждый атрибут является состоянием (State) для работы с процессом регистрации
    """
    name = State()        # Состояние для ввода имени пользователя
    forename = State()    # Состояние для ввода фамилии пользователя
    group = State()       # Состояние для ввода группы пользователя
    sex = State()         # Состояние для ввода пола пользователя
    notification_time = State()

class GamesForm(StatesGroup):
    """
    Класс, представляющий форму для игры или квиза
    
    Этот класс определяет состояния, связанные с играми или квизами:
        - keys: состояние для ввода ключевых слов или параметров игры
        - answers: состояние для ввода ответов на вопросы игры
        - sequence_game: состояние для игры с последовательностью

    Каждый атрибут является состоянием (State) для работы с процессом игры
    """
    keys = State()         # Состояние для ввода ключевых слов игры
    answers = State()      # Состояние для ввода ответов на вопросы
    answering = State()  # Состояние для игры с последовательностью
    new_question = State() # Для ожидания новой загадки
    
class DifficultyForm(StatesGroup):
    level = State()
    
def check_registration_state(state):
    """
    Функция для проверки, находится ли текущее состояние в процессе регистрации
    
    Аргументы:
        state (str): текущее состояние для проверки
        
    Возвращает:
        bool: True, если текущее состояние относится к регистрации, иначе False
    """
    return state in [
        RegistrationForm.name.state,
        RegistrationForm.forename.state,
        RegistrationForm.group.state,
        RegistrationForm.sex.state
    ]