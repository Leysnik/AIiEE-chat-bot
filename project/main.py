import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import config
from handlers import router, send_notifications
from db import make_session, User, History
import text
from states import check_registration_state

class DatabaseMiddleware(BaseMiddleware):
    """
    Промежуточное ПО для работы с базой данных. Сохраняет информацию о действиях пользователя в базе данных
    
    Аргументы:
        session (Session): Сессия для работы с базой данных
        
    Методы:
        __call__(handler, event, data): Основной метод, который перехватывает запросы, сохраняет данные в историю
        и проверяет регистрацию пользователя
    """
    def __init__(self, session) -> None:
        self.session = session

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        """
        Перехватывает каждый запрос и добавляет информацию о действии пользователя в базу данных
        
        Аргументы:
            handler (Callable): Основной обработчик события
            event (TelegramObject): Событие, которое вызвало обработку (например, сообщение от пользователя)
            data (Dict): Дополнительные данные, которые могут быть использованы в обработке
            
        Возвращает:
            Любой результат выполнения обработчика
        """
        chat_id = data['event_context'].chat.id
        session = self.session
        current_state = await data.get('state').get_state()
        msg = event.message
        callback = event.callback_query
        text_ = None
        type = 'other'
        if not msg is None:
            text_ = msg.text
            type = 'text'
        if not callback is None:
            text_ = callback.data
            type = 'callback'
        history = History(chat_id=chat_id, name=f'{data['event_context'].chat.first_name} {data['event_context'].chat.last_name}',
                          username=data['event_context'].chat.username, text=text_, type=type)
        session.add(history)
        session.commit()
        
        if session.query(User).filter(User.chat_id == chat_id).count() > 0 or \
           text_ in ['/register', '/stop'] or check_registration_state(current_state):
            with session as session:
                data['session'] = session
                return await handler(event, data)
        else:
            await bot.send_message(chat_id=chat_id, text=text.signup.format(name=msg.from_user.full_name))

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(router)

dp.update.middleware(DatabaseMiddleware(session=make_session()))

async def main():
    """
    Основная асинхронная функция для запуска бота, планировщика задач и обработки обновлений
    """
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        send_notifications,
        CronTrigger(hour=21, minute=53),
        kwargs={"bot": bot, "session": make_session()}
    )       

    scheduler.start()

    logging.info("bot is starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    logging.info("bot has stopped.")

if __name__ == "__main__":
    """
    Основная точка входа в программу. Настроена запись логов и запуск основного процесса
    """
    logging.basicConfig(level=logging.INFO, filename="bot.log", filemode='a', format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())