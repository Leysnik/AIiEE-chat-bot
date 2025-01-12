from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import flags
from aiogram.fsm.context import FSMContext
#from aiogram.utils.markdown import pre
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.state import State, StatesGroup

from utils import generate_text_yand, validate_group, validate_name
from daily_tasks import generate_daily_task
from states import RegistrationForm
import kb as kb
import text
from tips import tips
from db import User


router = Router()
        
dp = Dispatcher(storage=MemoryStorage())

# обработчик команды /start
@router.message(CommandStart()) 
async def start_handler(msg: Message, session):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)
    
@router.message(Command('register'), State(None))
async def register_user(msg: Message, state: FSMContext, session):
    if session.query(User).filter(User.chat_id == msg.chat.id).count() > 0:
        await msg.answer(text.already_registered)
        return
    await msg.answer(text.name_registration)
    await state.set_state(RegistrationForm.name)

@router.message(RegistrationForm.name)
async def register_ask_forename(msg: Message, state: FSMContext, session):
    name = msg.text
    if not validate_name(name):
        await msg.answer(text.error_registration)
        return
    await state.update_data(name=name)
    await msg.answer(text.forename_registration)
    await state.set_state(RegistrationForm.forename)

@router.message(RegistrationForm.forename)
async def register_ask_group(msg: Message, state: FSMContext, session):
    forename = msg.text
    if not validate_name(forename):
        await msg.answer(text.error_registration)
        return
    await state.update_data(forename=forename)
    await msg.answer(text.group_registration)
    await state.set_state(RegistrationForm.group)

@router.message(RegistrationForm.group)
async def register_end(msg: Message, state: FSMContext, session):
    group = msg.text
    if not validate_group(group):
        await msg.answer(text.error_registration)
        return
    await state.update_data(group=group)
    
    user_data = await state.get_data()
    user = User(chat_id=msg.chat.id, name=user_data['name'], \
                forename=user_data['forename'], group=user_data['group'])
    session.add(user)
    session.commit()
    await msg.answer(text.ending_registration)
    
    await state.clear()

# Обработчик нажатия кнопки "Советы"
@router.callback_query(F.data == 'tips')
async def tips_handler(msg: Message, session):
    await msg.message.answer(tips)

# Обработчик нажатия кнопки "Ежедневные задания"
@router.callback_query(F.data == 'daily_tasks')
async def daily_tasks_handler(msg: Message, session):
    res = generate_daily_task()
    await msg.message.answer(res)

# Обработчик нажатия кнопки "Помощь"
@router.callback_query(F.data == 'help')
async def daily_tasks_handler(msg: Message, session):
    res = generate_text_yand("Опиши очень коротко в паре предложений, что ты за бот")
    await msg.message.answer(res)

# обработчик нажатия кнопки "меню"
@router.message(F.text == "меню")
@router.message(F.text == "выйти в меню")
@router.message(F.text == "◀️ выйти в меню")
@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
@router.message(Command('menu'))
async def menu(msg: Message, session):
    await msg.answer(text.start.format(name=msg.from_user.full_name), reply_markup=kb.menu)

# обработчик сообщений
@router.message()
async def generate_reply(msg: Message, session):
    prompt = msg.text
    generated_text = generate_text_yand(prompt)
    if generated_text:
        await msg.answer(generated_text)
    else:
        await msg.answer("К сожалению, я не смог сгенерировать ответ.")
