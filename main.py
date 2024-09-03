from aiogram import Bot, Dispatcher, types
import asyncio
from handlers import router
import logging
from config import MAIN_API_TOKEN


bot = Bot(MAIN_API_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")