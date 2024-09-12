from aiogram import Router
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from handlers.handlers import db, bot
from keyboards import rek_keyboard, all_reklams, rm_reklam

admins = [5299011150, 7065054223]


admin_router = Router()


class RemoveReklamState(StatesGroup):
    waiting_rek_title = State()
    waiting_confirmation = State()


class AddReklamState(StatesGroup):
    waiting_rek_title = State()
    waiting_rek_href = State()
    waiting_rek_inline_text = State()


class AdStates(StatesGroup):
    waiting_for_ad = State()
    confirm_ad = State()


@admin_router.message(Command(commands="add"))
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


@admin_router.message(Command(commands=['reklama']))
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


@admin_router.message(AdStates.waiting_for_ad)
async def receive_ad(message: Message, state: FSMContext):
    # Сохраняем сообщение с рекламой во временное хранилище
    await state.update_data(ad_message_id=message.message_id)

    # Переходим в состояние подтверждения рекламы
    await state.set_state(AdStates.confirm_ad)

    # Отправляем сообщение с кнопками
    await message.answer("Проверьте свою рекламу:", reply_markup=rek_keyboard)


@admin_router.callback_query(AdStates.confirm_ad)
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


@admin_router.message(Command(commands=['add_reklama']))
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
@admin_router.message(AddReklamState.waiting_rek_title)
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
@admin_router.message(AddReklamState.waiting_rek_href)
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
@admin_router.message(AddReklamState.waiting_rek_inline_text)
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


# Команда для начала процесса удаления рекламы
@admin_router.message(Command(commands="rm_reklama"))
async def rm_reklama_command(message: Message, state: FSMContext):
    if message.from_user.id in admins:
        all_reklams_tuple = db.get_all_reklams()
        try:
            all_reklams_title = [item[0] for item in all_reklams_tuple]
        except TypeError:
            await message.answer("Нет доступной рекламы для удаления.")
        # Устанавливаем состояние ожидания выбора рекламы
        await state.set_state(RemoveReklamState.waiting_rek_title)

        # Отправляем пользователю список доступных реклам для удаления
        await message.answer("Выберите рекламу, которую хотите удалить:",
                             reply_markup=all_reklams(all_reklams_title))
    else:
        await message.answer("У вас нет прав")


# Хендлер для обработки выбора рекламы
@admin_router.message(RemoveReklamState.waiting_rek_title)
async def rm_state(message: Message, state: FSMContext):
    all_reklams_tuple = db.get_all_reklams()
    all_reklams_title = [item[0] for item in all_reklams_tuple]

    if message.text in all_reklams_title:
        # Сохраняем выбранную рекламу в состояние
        await state.update_data(selected_ad=message.text)

        # Запрашиваем подтверждение на удаление
        await message.answer("Подтвердите удаление", reply_markup=rm_reklam)
        await state.set_state(RemoveReklamState.waiting_confirmation)
    else:
        await message.answer("Выберите существующую рекламу.")


# Хендлер для обработки подтверждения или отмены удаления
@admin_router.callback_query(RemoveReklamState.waiting_confirmation)
async def confirm_removal(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_ad = user_data.get("selected_ad")

    if callback.data == "yes":
        # Удаляем рекламу из базы данных
        db.remove_reklam(selected_ad)
        await callback.message.edit_text(f"Реклама '{selected_ad}' удалена.")
    else:
        await callback.message.edit_text("Удаление отменено.")

    # Очищаем состояние
    await state.clear()
