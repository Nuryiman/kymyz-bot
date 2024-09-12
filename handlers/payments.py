from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import PreCheckoutQuery, Message, CallbackQuery, LabeledPrice

from handlers.handlers import db
from keyboards import price_kb

pay_router = Router()


@pay_router.message(Command(commands=['buy']))
async def price_list(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await message.answer(f"<a href='tg://openmessage?user_id={user_id}'>{first_name}</a>, бул жерден сиз кошумча аракет сатып алсаныз болот\n"
                         f"Керектуу сумманы танданыз:", reply_markup=price_kb, parse_mode='HTML')


@pay_router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@pay_router.message(F.successful_payment)
async def successful_payment(message: Message):
    if message.successful_payment.invoice_payload == "10stars":
        db.add_attempts(message.from_user.id, 5)
        await message.answer("Оплата успешна")

    elif message.successful_payment.invoice_payload == "20stars":
        db.add_attempts(message.from_user.id, 10)
        await message.answer("Оплата успешна")

    elif message.successful_payment.invoice_payload == "25stars":
        db.add_attempts(message.from_user.id, 15)
        await message.answer("Оплата успешна")


@pay_router.callback_query(F.data == "10stars")
async def pay_10_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="5 аракет",
                                          description="5 аракет сатып алуу",
                                          payload="10stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=1)])


@pay_router.callback_query(F.data == "20stars")
async def pay_20_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="10 аракет",
                                          description="10 аракет сатып алуу",
                                          payload="20stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=20)])


@pay_router.callback_query(F.data == "25stars")
async def pay_25_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="15 аракет",
                                          description="15 аракет сатып алуу",
                                          payload="25stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=25)])
