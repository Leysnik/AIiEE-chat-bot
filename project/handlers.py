from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import flags
from aiogram.fsm.context import FSMContext
import utils
from states import Gen
import kb as kb
import text

router = Router()

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

@router.message()
@flags.chat_action("typing")  # Показывает "набирает сообщение..."
async def generate_reply(msg: Message):
    prompt = msg.text
    try:
        # Генерация ответа с помощью модели
        generated_text = await utils.generate_text(prompt)
        if generated_text:
            # Добавляем форматирование для блока
            formatted_text = f"```\n{generated_text}\n```"
            await msg.answer(formatted_text, parse_mode="Markdown")  # Используем Markdown для блоков
        else:
            await msg.answer("К сожалению, я не смог сгенерировать ответ.", parse_mode="Markdown")
    except Exception as e:
        await msg.answer("Произошла ошибка при обработке сообщения.", parse_mode="Markdown")
        print(f"Ошибка: {e}")


    '''
    @router.callback_query(F.data == "generate_text")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.text_prompt)
    await clbck.message.edit_text(text.gen_text)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.exit_kb)

@router.message(Gen.text_prompt)
@flags.chat_action("typing")
async def generate_text(msg: Message, state: FSMContext):
    prompt = msg.text
    mesg = await msg.answer(text.gen_wait)
    res = await utils.generate_text(prompt)
    if not res:
        return await mesg.edit_text(text.gen_error, reply_markup=kb.iexit_kb)
    await mesg.edit_text(res[0] + text.text_watermark, disable_web_page_preview=True)
 

# обработчик для нажатия на кнопку "Ежедневные задания" 
@router.callback_query(F.data == "daily_tasks")
async def daily_tasks_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    task = generate_daily_task()  
    
    # отправка задания
    await callback_query.message.answer(task, reply_markup=kb.iexit_kb)
   '''