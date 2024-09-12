from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice

from handlers.handlers import db
from keyboards import *

call_router = Router()


@call_router.callback_query(F.data == "10stars")
async def pay_10_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="5 попыток",
                                          description="5 аракет сатып алуу",
                                          payload="10stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=2)])


@call_router.callback_query(F.data == "20stars")
async def pay_20_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="10 попыток",
                                          description="10 аракет сатып алуу",
                                          payload="20stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=20)])


@call_router.callback_query(F.data == "25stars")
async def pay_25_stars(callback: CallbackQuery):
    await callback.message.answer_invoice(title="15 попыток",
                                          description="15 аракет сатып алуу",
                                          payload="25stars",
                                          currency="XTR",
                                          prices=[LabeledPrice(label="XTR", amount=25)])


@call_router.callback_query(F.data.in_({"top_groups", "cancel_to_stat_group"}))
async def top_groups(callback: CallbackQuery):
    await callback.message.edit_text("Убакытты танданыз:", reply_markup=day_or_alltime_group_kb)


@call_router.callback_query(F.data.in_({"top_players", "cancel_to_stat"}))
async def top_users(callback: CallbackQuery):
    await callback.message.edit_text("Убакытты танданыз:", reply_markup=day_or_alltime_kb)


@call_router.callback_query(F.data == "users_all_time_top")
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


@call_router.callback_query(F.data == "users_day_top")
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
    await callback.message.edit_text(f"🥛🔝🥛Бир кундун ичиндеги глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}",
                                     reply_markup=cancel_to_users_top)


@call_router.callback_query(F.data == "groups_day_top")
async def top_groups_day(callback: CallbackQuery):
    top_users = db.get_day_top_groups()

    # Формируем строку с перечислением пользователей
    if top_users:
        user_statistic = "\n".join([
            f"{index + 1}. <a href='tg://resolve?domain={group[1]}'>{group[2]}</a> - {group[3]:.1f} литр"
            for index, group in enumerate(top_users)
        ])
    else:
        user_statistic = "Группада оюнчу жок"

    # Отправляем сообщение с информацией о топ-10 пользователях
    await callback.message.edit_text(f"🥛🔝🥛Бир кундун ичинде глобалдуу эн кымызды коп ичкен группалар:\n\n{user_statistic}",
                                     reply_markup=cancel_to_group_top, parse_mode='HTML')


@call_router.callback_query(F.data == "groups_all_time_top")
async def top_groups_all_top(callback: CallbackQuery):
    top_groups = db.get_top_groups()

    # Формируем строку с перечислением групп
    if top_groups:
        group_statistic = "\n".join([
            f"{index + 1}.<a href='tg://resolve?domain={group[1]}'>{group[2]}</a> - {group[3]:.1f} литр"
            for index, group in enumerate(top_groups)
        ])
    else:
        group_statistic = "Нет данных о группах."

    # Отправляем сообщение с информацией о топ-группах
    await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн кымызды коп ичкен группалар:\n\n{group_statistic}",
                                     reply_markup=cancel_to_group_top, parse_mode='HTML')


@call_router.callback_query(F.data == "cancel")
async def cancel_tops(callback: CallbackQuery):
    await callback.message.edit_text(text="Сиз каалаган топту танданыз", reply_markup=stat_kb)
