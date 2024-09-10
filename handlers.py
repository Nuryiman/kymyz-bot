from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery

from aiogram.filters.command import Command, CommandStart, CommandObject
from aiogram import Bot, F

from database import DataBase
import random

from config import MAIN_API_TOKEN
from keyboards import *

bot = Bot(MAIN_API_TOKEN)
router = Router()
db = DataBase(db_file="users.sqlite")
admins = [5299011150, 7065054223]
LOID = 7065054223


class AddReklamState(StatesGroup):
    waiting_rek_title = State()
    waiting_rek_href = State()
    waiting_rek_inline_text = State()


class AdStates(StatesGroup):
    waiting_for_ad = State()
    confirm_ad = State()


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
    chat_title = message.chat.title
    if chat_title == None:
        await message.answer('Салам! Мен кымыз бот. Башка оюнчулар менен биригип кымыз ичип жарыш.\n🥛🥛🥛\n\n'
                             'Кымыз ичуу учун /kymyz командасын жаз\n\n'
                             'Жардам - /help', reply_markup=add_bot_kb)

    else:
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
            db.add_group(group_id=message.chat.id, group_name=message.chat.title)
        else:
            await message.answer(f"@{user_name} Сизде аракет калбады\n Кийинки аракеттин жаралуусуна {get_time_attempts} калды")

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


@router.message(Command(commands=['my_stat']))
async def my_statistic(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    volume = db.get_volume(user_id=user_id)
    volume = round(volume, 1)
    await message.answer(f"@{user_name}, Сиз {volume} литр кымыз ичтиниз")


@router.message(Command(commands='stats'))
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


@router.message(Command(commands='top'))
async def choice_top(message: Message):
    await message.answer(text="Сиз каалаган топту танданыз", reply_markup=stat_kb)


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


@router.message(Command(commands=['reklama']))
async def start_ad(message: Message, state: FSMContext):
    if message.chat.title == None:
        if message.from_user.id in admins:
            # Устанавливаем состояние ожидания рекламы
            await state.set_state(AdStates.waiting_for_ad)
            await message.answer("Пожалуйста, отправьте сообщение с рекламой, которую хотите отправить.")
        else:
            await message.answer("У вас нет прав")
    else:
        await message.answer("Эту команду можно использовать только в <a href='t.me/emchek_bot'>ЛС</a> бота", parse_mode="HTML")


@router.message(AdStates.waiting_for_ad)
async def receive_ad(message: Message, state: FSMContext):
    # Сохраняем сообщение с рекламой во временное хранилище
    await state.update_data(ad_message_id=message.message_id)

    # Переходим в состояние подтверждения рекламы
    await state.set_state(AdStates.confirm_ad)

    # Отправляем сообщение с кнопками
    await message.answer("Проверьте свою рекламу:", reply_markup=rek_keyboard)


@router.callback_query(AdStates.confirm_ad)
async def process_ad_confirmation(callback: CallbackQuery, state: FSMContext):
    if callback.data == "not_send":
        await state.clear()
        await callback.message.edit_text("Отменено")
    if callback.data == "send_ad":
        # Получаем данные рекламы из состояния
        data = await state.get_data()
        ad_message_id = data.get("ad_message_id")

        # Копируем сообщение с рекламой получателю
        if ad_message_id:
            all_groups = db.get_all_groups()
            for item in all_groups:
                await bot.copy_message(
                    chat_id=item,
                    from_chat_id=callback.message.chat.id,
                    message_id=ad_message_id
                )
            await callback.message.answer("Реклама успешно отправлена!")
        else:
            await callback.message.answer("Ошибка: реклама не найдена.")

        # Завершаем состояние
        await state.clear()

    elif callback.data == "retry_ad":
        # Переводим в состояние ожидания новой рекламы
        await state.set_state(AdStates.waiting_for_ad)
        await callback.message.answer("Пожалуйста, отправьте новое сообщение с рекламой.")

    # Удаляем сообщение с кнопками после обработки
    await callback.message.delete()


@router.message(Command(commands=['add_reklama']))
async def add_reklama(message: Message, state: FSMContext):
    if message.chat.title == None:
        if message.from_user.id in admins:
            # Устанавливаем состояние ожидания рекламы
            await state.set_state(AddReklamState.waiting_rek_title)
            await message.answer("Пожалуйста, отправьте сообщение с рекламой, которую хотите отправить.")
        else:
            await message.answer("У вас нет прав")
    else:
        await message.answer("Эту команду можно использовать только в <a href='t.me/emchek_bot'>ЛС</a> бота",
                             parse_mode="HTML")


# Обработчик для получения названия рекламы
@router.message(AddReklamState.waiting_rek_title)
async def get_rek_title(message: Message, state: FSMContext):
    if message.text:
        # Сохраняем название рекламы во временное хранилище
        await state.update_data(rek_title=message.text)
        # Запрашиваем ссылку для рекламы
        await state.set_state(AddReklamState.waiting_rek_href)
        await message.answer("Отправьте ссылку для рекламы.")
    else:
        await state.set_state(AddReklamState.waiting_rek_title)
        await message.answer("Пожалуйста отправьте текстовое сообщение")


# Обработчик для получения ссылки на рекламу
@router.message(AddReklamState.waiting_rek_href)
async def get_rek_href(message: Message, state: FSMContext):
    if message.entities and message.text[0] != "@":
        # Сохраняем ссылку на рекламу
        await state.update_data(rek_href=message.text)
        # Запрашиваем текст кнопки
        await state.set_state(AddReklamState.waiting_rek_inline_text)
        await message.answer("Отправьте текст кнопки для рекламы.")
    else:
        await state.set_state(AddReklamState.waiting_rek_href)
        await message.answer("Это не ссылка. Пожалуйста отправьте ссылку")


# Обработчик для получения текста кнопки рекламы
@router.message(AddReklamState.waiting_rek_inline_text)
async def get_rek_inline_text(message: Message, state: FSMContext):
    if message.text:
        # Сохраняем текст кнопки
        await state.update_data(rek_inline_text=message.text)

        # Получаем все данные рекламы
        data = await state.get_data()
        rek_title = data.get('rek_title')
        rek_href = data.get('rek_href')
        rek_inline_text = data.get('rek_inline_text')

        # Здесь можно добавить логику сохранения рекламы в базе данных
        # Например, используя метод add_reklama класса Database
        db.add_reklama(rek_title, rek_href, rek_inline_text)

        await message.answer(f"Реклама добавлена:\n\n"
                             f"Название: {rek_title}\n"
                             f"Ссылка: {rek_href}\n"
                             f"Текст кнопки: {rek_inline_text}")

        # Сбрасываем состояние
        await state.clear()
    else:
        await state.set_state(AddReklamState.waiting_rek_inline_text)
        await message.answer("Пожалуйста отправьте текстовое сообщение")


@router.message(Command(commands=['buy']))
async def price_list(message: Message):

    await message.answer(f"{message.from_user.username}, бул жерден сиз кошумча аракет сатып алсаз болот\n"
                         f"Керектуу сумманы танданыз:", reply_markup=price_kb)


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


@router.callback_query(F.data == "10stars")
async def pay_10_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="5 попыток",
                                          description="5 аракет сатып алуу",
                                          payload="10stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=10)])


@router.callback_query(F.data == "20stars")
async def pay_20_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="10 попыток",
                                          description="10 аракет сатып алуу",
                                          payload="20stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=20)])


@router.callback_query(F.data == "25stars")
async def pay_25_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="15 попыток",
                                          description="15 аракет сатып алуу",
                                          payload="25stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=25)])


@router.callback_query(F.data.in_({"top_groups", "cancel_to_stat_group"}))
async def top_groups(callback: CallbackQuery):
    await callback.message.edit_text("Убакытты танданыз:", reply_markup=day_or_alltime_group_kb)


@router.callback_query(F.data.in_({"top_players", "cancel_to_stat"}))
async def top_users(callback: CallbackQuery):
    await callback.message.edit_text("Убакытты танданыз:", reply_markup=day_or_alltime_kb)


@router.callback_query(F.data == "users_all_time_top")
async def top_users_all_time(callback: CallbackQuery):
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
    await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}", reply_markup=cancel_to_users_top)


@router.callback_query(F.data == "users_day_top")
async def top_users_day(callback: CallbackQuery):
    top_users = db.get_global_day_top_users()

    # Формируем строку с перечислением пользователей
    if top_users:
        user_statistic = "\n".join([
            f"{index + 1}. {user[1]} - {user[2]:.1f} литр"
            for index, user in enumerate(top_users)
        ])
    else:
        user_statistic = "Группада оюнчу жок"

    # Отправляем сообщение с информацией о топ-10 пользователях
    await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}",
                                     reply_markup=cancel_to_users_top)


@router.callback_query(F.data == "groups_day_top")
async def top_groups_day(callback: CallbackQuery):
    top_users = db.get_global_day_top_users()

    # Формируем строку с перечислением пользователей
    if top_users:
        user_statistic = "\n".join([
            f"{index + 1}. {user[1]} - {user[2]:.1f} литр"
            for index, user in enumerate(top_users)
        ])
    else:
        user_statistic = "Группада оюнчу жок"

    # Отправляем сообщение с информацией о топ-10 пользователях
    await callback.message.edit_text(f"🥛🔝🥛Бир кундун ичинде глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}",
                                     reply_markup=cancel_to_group_top)


@router.callback_query(F.data == "groups_all_time_top")
async def top_groups_all_top(callback: CallbackQuery):
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
    await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн кымызды коп ичкен группалар:\n\n{group_statistic}",
                                     reply_markup=cancel_to_group_top)


@router.callback_query(F.data == "cancel")
async def cancel_tops(callback: CallbackQuery):
    await callback.message.edit_text(text="Сиз каалаган топту танданыз", reply_markup=stat_kb)
