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
    user_id = message.from_user.id
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
        db.add_volume(user_id=user_id, volume=random_volume)
        volume = db.get_volume(user_id=user_id)
        volume = round(volume, 1)
        await message.answer(f"@{user_name}, сиз {random_volume} литр кымыз ичтиниз\n Сиз ушу менен биригип {volume} ичтиниз")
    else:
        await message.answer(f"@{user_name} Сизде аракет калбады\n Кийинки аракеттин жаралуусуна {get_time_attempts} калды")
        print(db.get_all_users())


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


@router.message(Command(commands="add"))
async def admin_add_volume(message: Message, command: CommandObject):
    if message.from_user.id in admins:
        try:
            # Проверка, что аргументы предоставлены
            args = command.args
            if not args:
                await message.answer("Пожалуйста, укажите имя пользователя и количество попыток.")
                return

            args_list = args.split(" ")
            if len(args_list) < 2:
                await message.answer("Неверное количество аргументов. Используйте: /add <username> <attempts>")
                return

            user_name = args_list[0].lstrip('@')
            value = args_list[1]

            # Проверка, что количество попыток - целое число
            int_value = int(value)

            # Получение информации о пользователе
            db_user = db.get_user(user_name=user_name)
            if db_user is None:
                await message.answer(f"Пользователь с именем @{user_name} не найден.")
                return

            db_user_id = db_user[0]  # Извлечение user_id из кортежа

            # Добавление попыток пользователю
            db.add_attempts(user_id=db_user_id, attempts=int_value)
            await message.answer(f"Пользователю @{user_name} добавлено {int_value} попыток.")
        except ValueError:
            await message.answer("Количество попыток должно быть целым числом.")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}\nПожалуйста, введите правильное значение.")
