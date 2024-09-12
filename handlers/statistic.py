from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from handlers.handlers import db
from keyboards import add_bot_kb, stat_kb

stat_router = Router()


@stat_router.message(Command(commands=['my_stat']))
async def my_statistic(message: Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        volume = db.get_volume(user_id=user_id)
        volume = round(volume, 1)
        await message.answer(f"<a href='tg://openmessage?user_id={user_id}'>{first_name}</a>,"
                             f" Сиз {volume} литр кымыз ичтиниз", parse_mode='HTML')
    except TypeError:
        await message.answer("Сиз бир дагы жолу кымыз иче элексиз\n\n"
                             "/kymyz командасын жазып, азыр иче баштаныз")


@stat_router.message(Command(commands='stats'))
async def group_statistic(message: Message):
    chat_title = message.chat.title
    if chat_title == None:
        await message.answer("Салам! Мен кымыз бот. Башка оюнчулар менен биригип кымыз ичип жарыш.\n🥛🥛🥛\n\n"
                             'Кымыз ичуу учун /kymyz командасын жаз\n\n'
                             'Жардам - /help', reply_markup=add_bot_kb)
    else:
        # Получаем топ-10 пользователей с наибольшим volume
        top_users = db.get_group_users(group_id=message.chat.id)

        # Формируем строку с перечислением пользователей
        if top_users:
            user_statistic = "\n".join([
                f"{index + 1}. {user[1]} - {user[2]:.1f} литр"
                for index, user in enumerate(top_users)
            ])
        else:
            user_statistic = "Группада оюнчу жок"
        await message.answer(f"🔝Группадагы эн мыкты оюнчулар:\n\n{user_statistic}\n\n"
                             f"Группадагы топко кируу учун  /kymyz командасын терип кымыз иче баштаныз🥛")


@stat_router.message(Command(commands='top'))
async def choice_top(message: Message):
    await message.answer(text="Сиз каалаган топту танданыз", reply_markup=stat_kb)
