from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
# главное меню
menu = [
    [InlineKeyboardButton(text="📝 Ежедневные задания", callback_data="daily_tasks"),
     InlineKeyboardButton(text="🎮 Мини-игры", callback_data="mini_games")],
    [InlineKeyboardButton(text="📈 Прогресс", callback_data="progress"),
     InlineKeyboardButton(text="📚 Советы", callback_data="tips")],
    [InlineKeyboardButton(text="⚙️ Настройка сложности", callback_data="settings")],
    [InlineKeyboardButton(text="🏆 Соревнования", callback_data="challenges")],
   # [InlineKeyboardButton(text="💬 Поговорить на любую тему", callback_data="conversation")],
    [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)

# клавиатура для выхода в главное меню
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)

# инлайн-клавиатура для выхода в главное меню
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

def generate_keyboard_markup(names):
    builder = ReplyKeyboardBuilder()
    for name in names:
        builder.button(text=name)
    builder.adjust(2)
    markup = builder.as_markup()
    return markup
    

