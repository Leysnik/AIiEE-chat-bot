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

from utils import generate_text_yand
from states import Form
import kb as kb
import text

import json

router = Router()

listuser = {}

class User:
    def __init__(self, name):
        self.name = name
        self.code = ""
        
dp = Dispatcher(storage=MemoryStorage())


# Обработчик команды /start
@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

# Обработчик нажатия кнопки "меню"
@router.message(F.text == "меню")
@router.message(F.text == "выйти в меню")
@router.message(F.text == "◀️ выйти в меню")
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)

# Обработчик сообщений
@dp.message(F.text, Form.registered)
@router.message()
@flags.chat_action("typing")  
async def generate_reply(msg: Message):
    prompt = msg.text
    try:
        generated_text = await generate_text_yand(prompt)
       # print(generated_text.json())
        if generated_text:
           # formatted_text = pre(generated_text)
            await msg.answer(generated_text)
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