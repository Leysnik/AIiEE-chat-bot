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
from states import RegistrationForm
import kb as kb
import text
from db import User


router = Router()
        
dp = Dispatcher(storage=MemoryStorage())

# обработчик команды /start
@router.message(CommandStart()) 
async def start_handler(msg: Message, session):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)
    
@router.message(Command('register'), State(None))
async def register_user(msg: Message, state: FSMContext, session):
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

# Обработчик нажатия кнопки "Ежедневные задания"
@router.message(Command("daily_tasks"))
async def daily_tasks_handler(msg: Message, session):
    await msg.answer("Вы выбрали ежедневные задания.")

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
@flags.chat_action("typing")  
async def generate_reply(msg: Message, session):
    prompt = msg.text
    try:
        generated_text = await generate_text_yand(prompt)
        # print(generated_text.json())
        if generated_text:
           # formatted_text = pre(generated_text)
            await msg.answer(generated_text, parse_mode="Markdown")
        else:
            await msg.answer("К сожалению, я не смог сгенерировать ответ.")
    except Exception as e:
        await msg.answer("Произошла ошибка при обработке сообщения.")
        logging.error(f"Ошибка: {e}")
        


'''       
@dp.message(CommandStart(), State(None))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(f'Привет, {message.from_user.first_name}! Ваш id={message.from_user.id}\nВведите Ваше ФИО:')
    await state.update_data(lastfirstname=f'{message.from_user.last_name} {message.from_user.first_name}')
    await state.set_state(Form.name)


@dp.message(F.text, Form.name)
async def inputfio(message: Message, state: FSMContext):
    if len(message.text.split()) != 3:
        await message.answer(f'ФИО введено некорректно. Повторите ввод')
        return
    listuser[message.from_user.id] = User(message.text)
    await message.answer(f'ФИО принято! Введите номер группы:')
    await state.set_state(Form.code)


@dp.message(F.text, Form.code)
async def input_group(message: Message, state: FSMContext):
    if len(message.text.split()) != 1:
        await message.answer(f'Номер группы введен некорректно. Повторите ввод')
        return
    listuser[message.from_user.id].code = message.text
    await message.answer(f'Номер группы принят! Вы успешно зарегистрированы.')
    await state.set_state(Form.registered)
'''