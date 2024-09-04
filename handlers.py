from aiogram import Router
from aiogram.types import Message
from config import MAIN_API_TOKEN
from aiogram.filters.command import Command, CommandStart, CommandObject
from aiogram import Bot
from database import DataBase
import random


bot = Bot(MAIN_API_TOKEN)
router = Router()
db = DataBase(db_file="users.sqlite")
admins = [5299011150, 7065054223]


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
    get_time_attempts = db.get_time_until_next_attempt(user_id=user_id)
    if get_time_attempts == "Попытки уже доступны.":
        random_number = random.uniform(0, 5)
        random_volume = round(random_number, 1)
        added_volume = db.add_volume(user_id=user_id, volume=random_volume)
        volume = db.get_volume(user_id=user_id)
        volume = round(volume, 1)
        await message.answer(f"@{user_name}, сиз {random_volume} литр кымыз ичтиниз\n Сиз ушу менен биригип {volume} ичтиниз")
    else:
        await message.answer(f"@{user_name} Сизде аракет калбады\n Кийинки аракеттин жаралуусуна {get_time_attempts} калды")


@router.message(Command(commands=['my_stat']))
async def my_statistic(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    volume = db.get_volume(user_id=user_id)
    volume = round(volume, 1)
    await message.answer(f"@{user_name}, Сиз {volume} литр кымыз ичтиниз")


@router.message(Command(commands='stats'))
async def group_statistic(message: Message):
    pass


@router.message(Command(commands="add_volume"))
async def admin_add_volume(message: Message, command: CommandObject):
    if message.from_user.id in admins:
        args = command.args
        args_list = args.split(" ")
        user_name = args_list[0]
        volume = args_list[1]

        db.add_volume(user_id=db.get_user(user_name=user_name[1:-1]), volume=volume)
        await message.answer(f"Пользователю {user_name} добавлен {volume} попыток")
