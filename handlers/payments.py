from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import PreCheckoutQuery, Message

from handlers.handlers import db
from keyboards import price_kb

pay_router = Router()


@pay_router.message(Command(commands=['buy']))
async def price_list(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await message.answer(f"<a href='tg://openmessage?user_id={user_id}'>{first_name}</a>, бул жерден сиз кошумча аракет сатып алсаз болот\n"
                         f"Керектуу сумманы танданыз:", reply_markup=price_kb, parse_mode='HTML')


@pay_router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    print(query)
    await query.answer(True)


@pay_router.message(F.successful_payment)
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
