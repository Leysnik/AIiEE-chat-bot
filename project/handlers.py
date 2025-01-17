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

from utils import generate_text_yand, validate_name, validate_group
from daily_tasks import generate_words
from states import RegistrationForm, GamesForm
import kb
from kb import generate_keyboard_markup
import text
from db import User, update_daily_user_stats

router = Router()

dp = Dispatcher(storage=MemoryStorage())

'''
@router.message(Command("set_time"))
async def set_notification_time(message: Message, session):
    await message.answer("Введите время для уведомлений в формате HH:MM (например, 08:30).")

    # Установим состояние, чтобы обрабатывать следующий ответ
    await RegistrationForm.notification_time.set()


@router.message(StateFilter(RegistrationForm.notification_time))
async def save_notification_time(message: Message, state: FSMContext, session):
    try:
        # Проверяем, что время введено корректно
        time = message.text.strip()
        hour, minute = map(int, time.split(":"))
        
        # Сохраняем время в базе данных
        user = session.query(User).filter(User.chat_id == message.chat.id).first()
        user.notification_time = time
        session.commit()

        await message.answer(f"Время уведомлений установлено на {time}.")
    except ValueError:
        await message.answer("Некорректный формат времени. Пожалуйста, введите время в формате HH:MM.")
        
async def send_notifications(bot, session):
    """
    Отправляет уведомления пользователям в соответствии с их настройками времени.
    """
    users = session.query(User).filter(User.notifications_enabled == True).all()
    for user in users:
        try:
            await bot.send_message(user.chat_id, "Надо пройти ежедневное задание!")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user.chat_id}: {e}")
'''

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


@router.callback_query(lambda c: c.data == "start_riddle")
async def start_riddle_game(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик команды /start_riddle для начала игры с загадками.
    """
    await state.update_data(question_count=0) 
    
    rules = (
        "добро пожаловать в игру с загадками! 🧩\n\n"
        "правила игры:\n\n"
        "1. бот задаёт вам загадки. Ответ должен быть одним словом.\n"
        "2. если вы хотите получить подсказку, напишите 'подсказка'.\n"
        "3. если вы сдаётесь, напишите 'сдаюсь'. Бот выдаст правильный ответ и предложит новую загадку.\n"
        "4. на игру даётся 5 загадок, количество попыток на ответ не ограничено.\n"
        "5. не обижайтесь если у нашей нейросети не получилось хорошо сгенерировать загадку, она обязательно исправится!🤗\n\n"
        "Удачи! 🎉😉"
    )
    await callback_query.message.answer(rules)

    await generate_and_ask_question(callback_query.message, state)


async def generate_and_ask_question(message: types.Message, state: FSMContext):
    """
    Генерация новой загадки и отправка пользователю.
    """
    game_data = await state.get_data()
    question_count = game_data.get("question_count", 0)

    max_questions = 5
    if question_count >= max_questions:
        await message.answer(
            "вы ответили на все загадки!😃 Игра окончена. напишите /start_riddle для начала новой игры."
        )
        await state.finish()
        return

    prompt = """"Придумай загадку, которая подходит для людей любого возраста, но не является слишком простой или слишком сложной. Загадка должна быть логичной и однозначной. Ответ на загадку должен быть одним осмысленным словом.
                Загадка должна описывать объект или явление, которое легко узнаваемо, но не является очевидным с первого взгляда. Постарайся сделать загадку интересной, используя метафоры или элементы описания, 
                которые не слишком очевидны, но при этом легко воспринимаются.
                
                Пример формата:

                [Текст загадки] Ответ: [Ответ на загадку]

                Убедись, что ответ можно точно отгадать, и что его можно выразить одним словом. Убедись, что загадка не имеет подвоха и является логичной.
    
             """
    response = generate_text_yand(prompt)

    if "Ответ:" in response:
        question, correct_answer = response.split("Ответ:", 1)
        question = question.strip()
        correct_answer = correct_answer.strip()
    else:
        question = response
        correct_answer = "нейросеть не придумала ответ на эту загадку, простите, наша нейросеть ещё учится и может ошибаться 🫣"

    await state.update_data(
        current_question=question,
        correct_answer=correct_answer,
        question_count=question_count + 1,
    )
    await message.answer(f"загадка {question_count + 1}/{max_questions}: {question.replace("(", "").replace(")", "").replace("«", "").replace("»", "").replace("1", "").strip()}\n\nПопробуйте ответить!💅")
    await state.set_state(GamesForm.answering)


@router.message(GamesForm.answering)
async def handle_answer(msg: types.Message, state: FSMContext):
    """
    Обработка ответа пользователя на загадку.
    """
    user_answer = msg.text.strip().lower()

    if "подсказка" in user_answer:
        return await give_hint(msg, state)

    if "сдаюсь" in user_answer:
        game_data = await state.get_data()
        correct_answer = game_data.get("correct_answer", "нейросеть не придумала ответ на эту загадку, простите, наша нейросеть ещё учится и может ошибаться 🫣")
        correct_answer = correct_answer.replace("(", "").replace(")", "").replace(".", "").replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "")
        await msg.answer(f"вы сдались???🫨\nправильный ответ: {correct_answer}")
        return await generate_and_ask_question(msg, state)

    game_data = await state.get_data()
    correct_answer = game_data.get("correct_answer", "").lower().strip()

    if user_answer == correct_answer:
        await msg.answer("правильно! молодец!🙂")
        await generate_and_ask_question(msg, state)
    else:
        await msg.answer("не совсем 😔... попробуйте еще раз!")


async def give_hint(msg: types.Message, state: FSMContext):
    """
    Обрабатывает запрос на подсказку.
    """
    game_data = await state.get_data()
    current_question = game_data.get("current_question")

    if not current_question:
        await msg.answer("сначала начните игру с загадками.")
        return

    prompt = f"для загадки: '{current_question}', придумай подсказку."
    hint = generate_text_yand(prompt)
    await msg.answer(f"а подсказка такая: {hint}")


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
