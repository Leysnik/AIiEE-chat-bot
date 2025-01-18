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
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import types
import re

from utils import generate_text_yand, validate_name, validate_group, convert_latex_to_text
from daily_tasks import generate_words, generate_riddle
from states import RegistrationForm, GamesForm
import kb
from kb import generate_keyboard_markup
import text

router = Router()

dp = Dispatcher(storage=MemoryStorage())

async def send_notifications(bot, session):
    """
    Отправляет уведомления всем пользователям в базе данных о необходимости пройти ежедневное задание
    :param bot: объект бота для отправки сообщений
    :param session: сессия для работы с базой данных
    """
    session.upadate_daily_streak()
    users = session.get_users() 
    for user in users:
        try:
            await bot.send_message(user.chat_id, "надо пройти ежедневное задание!")
        except Exception as e:
            logging.error(f"не удалось отправить сообщение пользователю {user.chat_id}: {e}")
            session.delete_user(user.chat_id)

@router.callback_query(lambda call : call.data == 'progress')
async def stats_handler(call : CallbackQuery, session):
    stats = session.get_user_statistics(call.message.chat.id)
    ans = text.stats.format(daily_streak=stats['daily_streak'], daily_total=stats['daily_total'], \
                            games_total=stats['games_total'])
    await call.message.answer(ans)

@router.callback_query(lambda call : call.data == 'leaderboard')
async def stats_handler(call : CallbackQuery, session):
    users = session.get_best_users()
    users_ans = "\n".join([text.leaderboard_stroke.format(name=x, score=y) for x, y in users])
    ans = f'{text.leaderboard_header}{users_ans}'
    await call.message.answer(ans)

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
    if session.contains_user(msg.chat.id):
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
    session.commit_user(chat_id=msg.chat.id, name=user_data['name'], \
        forename=user_data['forename'], sex=user_data['sex'], group=user_data['group'])
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
async def stop_handler(msg: Message, state: FSMContext):
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
    res = generate_text_yand("напиши в паре предложений, что ты за бот. добавь что в твоём функционале есть ежедневные задания, ты можешь давать советы", callback.message.chat.id)
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
    if session.user_completed_daily(call.message.chat.id):
        await call.message.answer(text.already_completed_daily)
        return
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
        session.update_daily_user_stats(msg.chat.id, stats)
        await msg.answer(text.game_doubt.format(count=stats), reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    if len(keys) == 0:
        session.update_daily_user_stats(msg.chat.id, stats)
        await msg.answer(text.game_victory, reply_markup=ReplyKeyboardRemove())
        await state.clear()


@router.message(Command('start_riddle'))
async def start_riddle_game_command(message: Message, state: FSMContext):
    """
    Обработчик команды /start_riddle для начала игры с загадками через текстовую команду.
    """
    await state.update_data(question_count=0) 
    await message.answer(text.rules)

    await generate_and_ask_question(message, state)

@router.callback_query(lambda c: c.data == "start_riddle")
async def start_riddle_game(callback_query: types.CallbackQuery, state: FSMContext, session):
    """
    Обработчик команды /start_riddle для начала игры с загадками.
    """
    await state.update_data(question_count=0) 
    await callback_query.message.answer(text.rules)

    await generate_and_ask_question(callback_query.message, state, session)


async def generate_and_ask_question(message: types.Message, state: FSMContext, session):
    """
    Генерация новой загадки и отправка пользователю.
    """
    result = generate_riddle()
    if result is None:
        await message.answer(text.generate_error)
        return
    print(result)
    question_count = await state.get_value('question_count', 0) + 1
    if question_count > 3:
        game_total = await state.get_value('accept', 0)
        session.update_user_games(message.chat.id, game_total)
        await state.clear()
        await message.answer(text.game_completed)
        return
    
    await state.update_data(question_count=question_count)
    
    question = result[0]
    answer = result[1]
    
    await state.set_state(GamesForm.answering)
    await state.update_data(answer=answer, question=question)
    await message.answer(question)

@router.message(GamesForm.answering)
async def handle_answer(msg: types.Message, state: FSMContext, session):
    """
    Обработка ответа пользователя на загадку.
    """
    user_answer = msg.text.strip().lower()
    correct_answer = await state.get_value("answer")

    if "подсказка" == user_answer:
        return await give_hint(msg, state)

    if "сдаюсь" == user_answer:
        await msg.answer(f"вы сдались???🫨\nправильный ответ: {correct_answer}")
        await generate_and_ask_question(msg, state, session)
        return

    if user_answer == correct_answer:
        accept = await state.get_value('accept', 0) + 1
        await msg.answer("правильно! молодец!🙂")
        await state.update_data(accept=accept)
        await generate_and_ask_question(msg, state, session)
    else:
        await msg.answer("не совсем 😔... попробуйте еще раз!")


async def give_hint(msg: types.Message, state: FSMContext):
    """
    Обрабатывает запрос на подсказку.
    """
    game_data = await state.get_data()
    current_question = game_data.get("current_question")

    prompt = f"для загадки: '{current_question}', придумай подсказку."
    hint = generate_text_yand(prompt)
    await msg.answer(f"{hint}")

@router.message()
async def generate_reply(msg: Message):
    """
    Обрабатывает все сообщения, генерируя ответ с использованием текстового генератора.
    """
    prompt = msg.text
    generated_text = generate_text_yand(prompt, msg.chat.id)
    if generated_text:
        clean_text = convert_latex_to_text(generated_text)
        await msg.answer(clean_text, parse_mode='Markdown')
    else:
        await msg.answer(text.generate_error)


'''
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
        await msg.answer(generated_text, parse_mode='Markdown')
    else:
        await msg.answer(text.generate_error)
'''