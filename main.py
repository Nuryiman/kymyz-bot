import logging

from aiogram import Bot, Dispatcher
import asyncio

from handlers.for_admin import admin_router
from handlers.payments import pay_router
from handlers.callbacks import call_router
from handlers.handlers import router
from config import MAIN_API_TOKEN
from handlers.statistic import stat_router

bot = Bot(MAIN_API_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_routers(router, call_router, pay_router, stat_router, admin_router)
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
