from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Главное меню
menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Ежедневные задания", callback_data="daily_tasks"),
     InlineKeyboardButton(text="🎮 Мини-игра", callback_data="start_riddle")],
    [InlineKeyboardButton(text="📈 Прогресс", callback_data="progress"),
     InlineKeyboardButton(text="📚 Советы", callback_data="tips")],
    #[InlineKeyboardButton(text="⚙️ Настройка сложности", callback_data="settings")],
    [InlineKeyboardButton(text="🏆 Соревнования", callback_data="challenges")],
    [InlineKeyboardButton(text="⏰ Установить время уведомлений", callback_data="choose_time")],
    [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]
])
#menu = InlineKeyboardMarkup(inline_keyboard=menu)
"""
Главное меню бота с кнопками для различных разделов, таких как:
    - Ежедневные задания
    - Мини-игры
    - Прогресс
    - Советы
    - Настройка сложности
    - Соревнования
    - Помощь

Каждая кнопка привязана к определенному callback_data, который будет использован для обработки действий пользователя
"""
# Клавиатура для выхода в главное меню
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
"""
Клавиатура для возвращения в главное меню, которая будет показываться пользователю в виде обычной кнопки "Выйти в меню"
"""

# Инлайн-клавиатура для выхода в главное меню
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])
"""
Инлайн-клавиатура с кнопкой "Выйти в меню", которая использует callback_data для навигации
"""

def generate_keyboard_markup(names):
    """
    Функция для создания клавиатуры с динамическими кнопками

    Аргументы:
        names (list): Список строк, который будет использоваться для создания кнопок

    Возвращает:
        markup (ReplyKeyboardMarkup): Клавиатура с кнопками
    """
    builder = ReplyKeyboardBuilder()
    for name in names:
        builder.button(text=name)
    builder.adjust(2)  # Клавиши будут разделены на 2 столбца
    markup = builder.as_markup()
    return markup
"""
Функция generate_keyboard_markup позволяет создать клавиатуру с динамическим набором кнопок, 
которые передаются через список `names`. Каждая кнопка будет иметь текст из элементов списка
Функция использует ReplyKeyboardBuilder для формирования клавиатуры и возвращает готовую клавиатуру как объект ReplyKeyboardMarkup
"""
