from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State
import asyncio

from utils import generate_text_yand, validate_name, validate_group
from daily_tasks import generate_words
from states import RegistrationForm, GamesForm
import kb
from kb import generate_keyboard_markup
import text
from db import User, update_daily_user_stats

router = Router()

dp = Dispatcher(storage=MemoryStorage())

async def send_notifications(bot, session):
    """
    Отправляет уведомления всем пользователям в базе данных о необходимости пройти ежедневное задание
    :param bot: объект бота для отправки сообщений
    :param session: сессия для работы с базой данных
    """
    users = session.query(User).all()
    for user in users:
        try:
            await bot.send_message(user.chat_id, "надо пройти ежедневное задание!")
        except Exception as e:
            logging.error(f"не удалось отправить сообщение пользователю {user.chat_id}: {e}")

@router.message(F.text == "меню")
@router.message(F.text == "выйти в меню")
@router.message(F.text == "◀️ выйти в меню")
@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
@router.message(Command('menu'))
async def menu(msg: Message):
    """
    Обработчик нажатия кнопки "Меню". Отправляет пользователю приветственное сообщение и клавиатуру меню
    :param msg: сообщение от пользователя
    """
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

@router.message(Command('register'), State(None))
async def register_user(msg: Message, state: FSMContext, session):
    """
    Обработчик команды /register. Запускает процесс регистрации нового пользователя
    :param msg: сообщение от пользователя
    :param state: состояние FSM для отслеживания этапов регистрации
    :param session: сессия для работы с базой данных
    """
    if session.query(User).filter(User.chat_id == msg.chat.id).count() > 0:
        await msg.answer(text.already_registered)
        return
    await msg.answer(text.name_registration)
    await state.set_state(RegistrationForm.name)

@router.message(RegistrationForm.name)
async def register_ask_forename(msg: Message, state: FSMContext, session):
    """
    Запрашивает у пользователя имя для регистрации
    :param msg: сообщение от пользователя
    :param state: состояние FSM
    :param session: сессия для работы с базой данных
    """
    name = msg.text
    if not validate_name(name):
        await msg.answer(text.error_registration)
        return
    await state.update_data(name=name)
    await msg.answer(text.forename_registration)
    await state.set_state(RegistrationForm.forename)

@router.message(RegistrationForm.forename)
async def register_ask_gender(msg: Message, state: FSMContext, session):
    """
    Запрашивает у пользователя фамилию для регистрации
    :param msg: сообщение от пользователя
    :param state: состояние FSM
    :param session: сессия для работы с базой данных
    """
    forename = msg.text
    if not validate_name(forename):
        await msg.answer(text.error_registration)
        return
    await state.update_data(forename=forename)
    await msg.answer(text.gender_registration)
    await state.set_state(RegistrationForm.sex)

@router.message(RegistrationForm.sex)
async def register_ask_group(msg: Message, state: FSMContext, session):
    """
    Запрашивает у пользователя пол для регистрации
    :param msg: сообщение от пользователя
    :param state: состояние FSM
    :param session: сессия для работы с базой данных
    """
    sex = msg.text.lower()
    if not sex in ['мужской', 'женский']:
        await msg.answer(text.error_registration)
        return
    await state.update_data(sex=sex)
    await msg.answer(text.group_registration)
    await state.set_state(RegistrationForm.group)

@router.message(RegistrationForm.group)
async def register_end(msg: Message, state: FSMContext, session):
    """
    Завершается процесс регистрации и сохраняются данные пользователя
    :param msg: сообщение от пользователя
    :param state: состояние FSM
    :param session: сессия для работы с базой данных
    """
    group = msg.text.lower()
    if not validate_group(group):
        await msg.answer(text.error_registration)
        return
    await state.update_data(group=group)

    user_data = await state.get_data()
    user = User(chat_id=msg.chat.id, name=user_data['name'], \
        forename=user_data['forename'], sex=user_data['sex'], group=user_data['group'])
    session.add(user)
    session.commit()
    await msg.answer(text.ending_registration)
    await state.clear()

@router.message(CommandStart())
async def start_handler(msg: Message):
    """
    Обработчик команды /start. Отправляет приветственное сообщение с клавиатурой меню
    :param msg: сообщение от пользователя
    :param session: сессия для работы с базой данных
    """
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

@router.message(Command('stop'))
async def start_handler(msg: Message, state: FSMContext):
    """
    Обработчик команды /stop. Завершается состояние FSM и отправляется сообщение о завершении
    :param msg: сообщение от пользователя
    :param session: сессия для работы с базой данных
    :param state: состояние FSM
    """
    if state is None:
        await msg.answer(text.error_state)
        return
    else:
        await msg.answer(text.stop_state)
    await state.clear()

@router.callback_query(F.data == 'tips')
async def tips_handler(callback: Message):
    """
    Обработчик нажатия кнопки "Советы". Отправляет пользователю текст с советами
    :param callback: объект обратного вызова от кнопки
    """
    res = generate_text_yand("напиши несколько советов для улучшения памяти. используй только алфавит, цифры и знаки Markdown", callback.message.chat.id)
    if res is None:
        await callback.answer(text.generate_error)
        return
    await callback.message.answer(res, parse_mode="Markdown")

@router.callback_query(F.data == 'help')
async def help_handler(callback: Message):
    """
    Обработчик нажатия кнопки "Помощь". Отправляет пользователю информацию о боте
    :param callback: объект обратного вызова от кнопки
    """
    res = generate_text_yand("напиши в паре предложений, что ты за бот", callback.message.chat.id)
    if res is None:
        await callback.answer(text.generate_error)
        return
    await callback.message.answer(res)

@router.callback_query(F.data == 'daily_tasks', State(None))
async def daily_tasks_handler(call: CallbackQuery, state: FSMContext, session):
    """
    Обработчик нажатия кнопки "Ежедневные задания". Отправляет задание пользователю и запускает игру
    :param call: объект обратного вызова от кнопки
    :param state: состояние FSM
    :param session: сессия для работы с базой данных
    """
    if session.query(User).filter(User.chat_id == call.message.chat.id).one().daily_complete == 1:
        await call.message.answer(text.already_completed_daily)
    words = generate_words(5)
    incorrect_words = generate_words(5)
    if words is None or incorrect_words is None:
        await call.message.answer(text.generate_error)
        return
    await state.set_state(GamesForm.keys)
    await state.update_data(keys=words)
    message = await call.message.answer(text.game_msg.format(words=words))
    await run_game(message, state, words, incorrect_words)

async def run_game(message: Message, state, words, incorrect_words):
    """
    Запускает игру с пользователем, показывая слова и ожидая их ответы
    :param message: сообщение, содержащее информацию о заданиях
    :param state: состояние FSM
    :param words: список правильных слов
    :param incorrect_words: список неправильных слов
    """
    total_words = set(words + incorrect_words)
    await asyncio.sleep(5)
    await message.bot.edit_message_text(
        text=text.game_msg.format(words=''),
        chat_id=message.chat.id,
        message_id=message.message_id
    )
    await state.set_state(GamesForm.answers)
    await state.update_data(attempts=5)
    await message.answer(text.start_game, reply_markup=generate_keyboard_markup(total_words))

@router.message(GamesForm.answers)
async def game_answers_handler(msg: Message, state: FSMContext, session):
    """
    Обрабатывает ответы игрока в игре, проверяя правильность слов и количество попыток
    :param msg: сообщение с ответом игрока
    :param state: состояние FSM
    :param session: сессия для работы с базой данных
    """
    word = msg.text
    keys = await state.get_value('keys')
    stats = await state.get_value('stats', 0)
    attempts = await state.get_value('attempts') - 1
    goal = False
    if word in keys:
        keys.remove(word)
        stats += 1
        goal = True
    if goal:
        await state.update_data(stats=stats)
        await msg.answer(text.game_correct_word)
    else:
        await msg.answer(text.game_wrong_words)

    await state.update_data(keys=keys, attempts=attempts, stats=stats)
    if len(keys) != 0 and attempts == 0:
        update_daily_user_stats(session, msg.chat.id, stats)
        await msg.answer(text.game_doubt.format(count=stats), reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    if len(keys) == 0:
        update_daily_user_stats(session, msg.chat.id, stats)
        await msg.answer(text.game_victory, reply_markup=ReplyKeyboardRemove())
        await state.clear()

@router.message()
async def generate_reply(msg: Message):
    """
    Обрабатывает все сообщения, генерируя ответ с использованием текстового генератора
    :param msg: сообщение от пользователя
    :param session: сессия для работы с базой данных
    """
    prompt = msg.text
    generated_text = generate_text_yand(prompt, msg.chat.id)
    if generated_text:
        await msg.answer(generated_text)
    else:
        await msg.answer(text.generate_error)
