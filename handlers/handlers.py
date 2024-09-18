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
db = DataBase(db_file="users.sqlite")
admins = [5299011150, 7065054223]
BOT_ID = 7392413904
LOID = 7065054223


@router.message(F.new_chat_members)
async def new_chat_member_handler(message: Message):
    new_members = message.new_chat_members

    for member in new_members:
        if member.id == message.from_user.id:
            # Пользователь присоединился по ссылке
            welcome_text = (f"<a href='tg://openmessage?user_id={member.id}'>{member.first_name}</a>, "
                            f"добро пожаловать в группу! Кымыздан ал🥛\n"
                            f"(/kymyz командасын жаз)")
        else:
            # Пользователя добавили
            welcome_text = (f"<a href='tg://openmessage?user_id={member.id}'>{member.first_name}</a>, "
                            f"вас добавили в группу! Кымыздан ал🥛\n"
                            f"(/kymyz командасын жаз)")

        await message.answer(welcome_text, parse_mode="HTML")

    # Регистрация группы в базе данных
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
                                 f" Кийинки аракеттин жаралуусуна {get_time_attempts} калды\n\n"
                                 f"Кошумча аракеттер - /buy", parse_mode='HTML')

    if random.randint(1, 5) == 1:
        all_reklams = db.get_all_reklams()
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


@router.message(F.text.lower() == "ичируу")
async def rp(message: Message):
    if message.chat.title is None:
        await message.answer('Салам! Мен кымыз бот. Башка оюнчулар менен биригип кымыз ичип жарыш.\n🥛🥛🥛\n\n'
                     'Кымыз ичуу учун /kymyz командасын жаз\n\n'
                     'Жардам - /help', reply_markup=add_bot_kb)
    else:
        if message.reply_to_message:
            reply_msg = message.reply_to_message
            reply_id = reply_msg.from_user.id
            reply_first_name = reply_msg.from_user.first_name
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            await message.answer(f"<a href='tg://openmessage?user_id={user_id}'>{first_name}</a> кымыз ичирди"
                                 f" <a href='tg://openmessage?user_id={reply_id}'>{reply_first_name}</a>",
                                 parse_mode='HTML')
        else:
            await message.answer("Бул команда бироого жооп бергенде гана иштейт")


@router.message(Command(commands="help"))
async def help_command(message: Message):
    await message.answer("""
    Бот менен кантип баштоо керек?
- Сиз группага бот кошуу керек (чат)

Бот буйруктары:
/start - ботту баштоо
/kymyz - оюнду баштоо
/stats - группадагы статистика
/top - мыкты оюнчулар жана группалар
/buy - аракет кошуу
/help - бот жардам
Ичируу - кымыз менен сыйлоо
    """)


@router.message(F.reply_to_message)
async def add_bot_stop(message: Message):
    if message.text is not None:
        original_text = message.text.lower()
        if original_text == "бот стоп":
            user_username = message.from_user.username
            user_id = message.from_user.id
            user_first_name = message.from_user.first_name
            reply_username = message.reply_to_message.from_user.username
            reply_id = message.reply_to_message.from_user.id
            reply_first_name = message.reply_to_message.from_user.first_name
            successful_bot_stop = db.add_or_rm_bot_stop(prohibiting_user_id=user_id,
                                                        prohibiting_username=user_username,
                                                        prohibiting_user_first_name=user_first_name,
                                                        prohibited_username=reply_username,
                                                        prohibited_user_id=reply_id,
                                                        prohibited_user_first_name=reply_first_name)
            if successful_bot_stop == "Бот стоп добавлен":
                await message.answer(f"{reply_first_name} Сизге {user_first_name} жооп берууго тыйуу салды")
            elif successful_bot_stop == "Бот стоп убран":
                await message.answer(f"{reply_first_name} Сизге {user_first_name} жооп берууго уруксат берди")
            else:
                await message.answer(f"{reply_first_name} Бот стоптон коргоо бар")

    else:
        user_id = message.from_user.id
        reply_id = message.reply_to_message.from_user.id
        is_allowed = db.get_reply_permissions(user_id=user_id, reply_user_id=reply_id)
        if is_allowed == "запрещено":
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except Exception:
                pass
