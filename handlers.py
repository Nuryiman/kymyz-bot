from aiogram import Router
from aiogram.types import Message
from config import MAIN_API_TOKEN
from aiogram.filters.command import Command, CommandStart
from aiogram import Bot
from database import DataBase
import random


bot = Bot(MAIN_API_TOKEN)
router = Router()
db = DataBase(db_file="users.sqlite")


@router.message(CommandStart())
async def start(message: Message):
    user_id = message.chat.id
    user_name = message.from_user.username
    db.add_user(user_id=user_id, user_name=user_name)
    await message.answer('Hello')


@router.message(Command(commands=['kymyz']))
async def drink_kymyz(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    db.add_user(user_id=user_id, user_name=user_name)
    random_number = random.uniform(0, 5)
    random_volume = round(random_number, 1)
    db.add_volume(user_id=user_id, volume=random_volume)
    volume = db.get_volume(user_id=user_id)
    volume = round(volume, 1)
    await message.answer(f"@{user_name}, сиз {random_volume} литр кымыз ичтиниз\n Сиз ушу менен биригип {volume} ичтиниз")


@router.message(Command(commands='my_stat'))
async def my_statistic(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    volume = db.get_volume(user_id=user_id)
    volume = round(volume, 1)
    await message.answer(f"@{user_name}, Сиз {volume} литр кымыз ичтиниз")


@router.message(Command(commands='stats'))
async def group_statistic(message: Message):
    pass