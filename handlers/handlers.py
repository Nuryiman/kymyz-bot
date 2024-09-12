from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart
from aiogram import Bot, F

from database import DataBase
import random

from config import MAIN_API_TOKEN
from keyboards import *

bot = Bot(MAIN_API_TOKEN)
router = Router()
db = DataBase(db_file="../users.sqlite")
admins = [5299011150, 7065054223]
LOID = 7065054223


@router.message(F.new_chat_member)
async def new_chat_member_handler(message: Message):
    await message.answer(f"<a href='tg://openmessage?user_id={message.from_user.id}'>{message.from_user.first_name}</a>, Кымыздан ал🥛\n"
                         f"(/kymyz командасын жаз)", parse_mode="HTML")
    db.add_group(group_id=message.chat.id, group_username=message.chat.username, group_name=message.chat.title)


@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    first_name = message.from_user.first_name
    db.add_user(user_id=user_id, user_name=user_name, first_name=first_name)
    await message.answer('Салам! Мен кымыз бот. Башка оюнчулар менен биригип кымыз ичип жарыш.\n🥛🥛🥛\n\n'
                         'Кымыз ичуу учун /kymyz командасын жаз\n\n'
                         'Жардам - /help', reply_markup=add_bot_kb)
    db.add_group(group_id=message.chat.id, group_username=message.chat.username, group_name=message.chat.title)


@router.message(Command(commands=['kymyz']))
async def drink_kymyz(message: Message):
    chat_title = message.chat.title
    if chat_title == None:
        await message.answer('Салам! Мен кымыз бот. Башка оюнчулар менен биригип кымыз ичип жарыш.\n🥛🥛🥛\n\n'
                             'Кымыз ичуу учун /kymyz командасын жаз\n\n'
                             'Жардам - /help', reply_markup=add_bot_kb)

    else:
        user_id = message.from_user.id
        user_name = message.from_user.username
        first_name = message.from_user.first_name
        db.add_user(user_id=user_id, user_name=user_name, first_name=first_name)
        get_time_attempts = db.get_time_until_next_attempt(user_id=user_id)
        if get_time_attempts == "Попытки уже доступны.":
            random_number = random.uniform(0, 5)
            random_volume = round(random_number, 1)
            db.add_volume(user_id=user_id, volume=random_volume)
            volume = db.get_volume(user_id=user_id)
            volume = round(volume, 1)
            db.add_user_to_group(user_id=user_id, group_id=message.chat.id)
            await message.answer(f"<a href='tg://openmessage?user_id={user_id}'>{first_name}</a>, сиз {random_volume} литр кымыз ичтиниз\n"
                                 f"Сиз ушу менен биригип {volume} ичтиниз", parse_mode='HTML')
            db.add_group(group_id=message.chat.id, group_username=message.chat.username, group_name=message.chat.title)
        else:
            await message.answer(f"<a href='tg://openmessage?user_id={user_id}'>{first_name}</a> Сизде аракет калбады\n"
                                 f" Кийинки аракеттин жаралуусуна {get_time_attempts} калды", parse_mode='HTML')

    random_number = random.randint(1, 5)
    if random.randint(1, 5) == 1:
        all_reklams = db.get_all_reklams()
        print(all_reklams)
        if all_reklams:
            random_rek = random.choice(all_reklams)
            rek_title = random_rek[0]
            rek_href = random_rek[1]
            button_text = random_rek[2]

            await message.answer(
                f"<a href='{rek_href}'>{rek_title}</a>",
                parse_mode="HTML",
                reply_markup=rek_kb(text=button_text, url=rek_href)
            )
