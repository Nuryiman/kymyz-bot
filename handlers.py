from aiogram import Router
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery

from aiogram.filters.command import Command, CommandStart, CommandObject
from aiogram import Bot, F
from database import DataBase
import random

from config import MAIN_API_TOKEN
from keyboards import price_kb, stat_kb

bot = Bot(MAIN_API_TOKEN)
router = Router()
db = DataBase(db_file="users.sqlite")
admins = [5299011150, 7065054223]
LOID = 7065054223


@router.message(F.new_chat_member)
async def new_chat_member_handler(message: Message):
    await message.answer(f"<a href='tg://resolve?domain={message.from_user.username}'>{message.from_user.first_name}</a>, Кымыздан ал🥛\n"
                         f"(/kymyz командасын жаз)", parse_mode="HTML")
    db.add_group(group_id=message.chat.id, group_name=message.chat.first_name)


@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    db.add_user(user_id=user_id, user_name=user_name)
    await message.answer('Салам! Мен кымыз бот. Башка оюнчулар менен биригип кымыз ичип жарыш.\n🥛🥛🥛\n\n'
                         'Кымыз ичуу учун /kymyz командасын жаз\n\n'
                         'Жардам - /help')
    db.add_group(group_id=message.chat.id, group_name=message.chat.title)


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
        db.add_user_to_group(user_id=user_id, group_id=message.chat.id)
        await message.answer(f"@{user_name}, сиз {random_volume} литр кымыз ичтиниз\n"
                             f"Сиз ушу менен биригип {volume} ичтиниз")
    else:
        await message.answer(f"@{user_name} Сизде аракет калбады\n Кийинки аракеттин жаралуусуна {get_time_attempts} калды")
        print(db.get_all_users())
    random_rek = random.randint(1, 10)
    if random_rek == 1:
        await message.answer("<a href='tg://resolve?domain=malibuxs'>Глянь на канал</a>", parse_mode="HTML")


@router.message(Command(commands=['my_stat']))
async def my_statistic(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    volume = db.get_volume(user_id=user_id)
    volume = round(volume, 1)
    await message.answer(f"@{user_name}, Сиз {volume} литр кымыз ичтиниз")


@router.message(Command(commands='stats'))
async def group_statistic(message: Message):
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


@router.message(Command(commands='top'))
async def choice_top(message: Message):
    await message.answer(text="Сиз каалагн топту танданыз", reply_markup=stat_kb)


@router.callback_query(F.data == "top_players")
async def group_statistic(callback: CallbackQuery):
    # Получаем топ-10 пользователей с наибольшим volume
    top_users = db.get_global_top_users()

    # Формируем строку с перечислением пользователей
    if top_users:
        user_statistic = "\n".join([
            f"{index + 1}. {user[1]} - {user[2]:.1f} литр"
            for index, user in enumerate(top_users)
        ])
    else:
        user_statistic = "Группада оюнчу жок"

    # Отправляем сообщение с информацией о топ-10 пользователях
    await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}")


@router.callback_query(F.data == "top_groups")
async def top_groups(callback: CallbackQuery):
    # Получаем топ-группы по суммарному объему
    top_groups = db.get_top_groups()

    # Формируем строку с перечислением групп
    if top_groups:
        group_statistic = "\n".join([
            f"{index + 1}.{group[1]} - {group[2]:.1f} литр"
            for index, group in enumerate(top_groups)
        ])
    else:
        group_statistic = "Нет данных о группах."

    # Отправляем сообщение с информацией о топ-группах
    await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн кымызды коп ичкен группалар:\n\n{group_statistic}")


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


@router.message(Command(commands=['buy']))
async def price_list(message: Message):

    await message.answer(f"{message.from_user.username}, бул жерден сиз кошумча аракет сатып алсаз болот\n"
                         f"Керектуу сумманы танданыз:", reply_markup=price_kb)


@router.callback_query()
async def payment(callback: CallbackQuery):
    if callback.data == "10stars":
        await callback.message.answer_invoice(title="5 попыток",
                                              description="5 аракет сатып алуу",
                                              payload="10stars",
                                              currency="XTR",
                                              prices=[LabeledPrice(label="XTR", amount=10)])

    if callback.data == "20stars":
        await callback.message.answer_invoice(title="10 попыток",
                                              description="10 аракет сатып алуу",
                                              payload="20stars",
                                              currency="XTR",
                                              prices=[LabeledPrice(label="XTR", amount=20)])

    if callback.data == "25stars":
        await callback.message.answer_invoice(title="15 попыток",
                                              description="15 аракет сатып алуу",
                                              payload="25stars",
                                              currency="XTR",
                                              prices=[LabeledPrice(label="XTR", amount=25)])


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    print(query)
    await query.answer(True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    if message.successful_payment.payload == "10stars":
        print(f"Successful payment ID: {message.successful_payment.telegram_payment_charge_id}")
        db.add_attempts(message.from_user.id, 5)
        await message.answer("Оплата успешна")

    if message.successful_payment.payload == "20stars":
        print(f"Successful payment ID: {message.successful_payment.telegram_payment_charge_id}")
        db.add_attempts(message.from_user.id, 10)
        await message.answer("Оплата успешна")

    if message.successful_payment.payload == "25stars":
        print(f"Successful payment ID: {message.successful_payment.telegram_payment_charge_id}")
        db.add_attempts(message.from_user.id, 15)
        await message.answer("Оплата успешна")
