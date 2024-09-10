# from aiogram import Router
# from aiogram.types import CallbackQuery
#
# router = Router()
#
# @router.callback_query()
# async def top_groups(callback: CallbackQuery):
#     try:
#         if callback.data == "10stars":
#             await callback.message.answer_invoice(title="5 попыток",
#                                                   description="5 аракет сатып алуу",
#                                                   payload="10stars",
#                                                   currency="XTR",
#                                                   prices=[LabeledPrice(label="XTR", amount=10)])
#
#         if callback.data == "20stars":
#             await callback.message.answer_invoice(title="10 попыток",
#                                                   description="10 аракет сатып алуу",
#                                                   payload="20stars",
#                                                   currency="XTR",
#                                                   prices=[LabeledPrice(label="XTR", amount=20)])
#
#         if callback.data == "25stars":
#             await callback.message.answer_invoice(title="15 попыток",
#                                                   description="15 аракет сатып алуу",
#                                                   payload="25stars",
#                                                   currency="XTR",
#                                                   prices=[LabeledPrice(label="XTR", amount=25)])
#
#         if callback.data == "top_groups" or "cancel_to_stat_group":
#             await callback.message.edit_text("Убакытты танданыз:", reply_markup=day_or_alltime_group_kb)
#
#         if callback.data == "top_players" or "cancel_to_stat":
#             await callback.message.edit_text("Убакытты танданыз:", reply_markup=day_or_alltime_kb)
#
#         if callback.data == "users_all_time_top":
#             top_users = db.get_global_top_users()
#
#             # Формируем строку с перечислением пользователей
#             if top_users:
#                 user_statistic = "\n".join([
#                     f"{index + 1}. {user[1]} - {user[2]:.1f} литр"
#                     for index, user in enumerate(top_users)
#                 ])
#             else:
#                 user_statistic = "Группада оюнчу жок"
#
#             # Отправляем сообщение с информацией о топ-10 пользователях
#             await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}", reply_markup=cancel_to_users_top)
#
#         if callback.data == "users_day_top":
#             top_users = db.get_global_day_top_users()
#
#             # Формируем строку с перечислением пользователей
#             if top_users:
#                 user_statistic = "\n".join([
#                     f"{index + 1}. {user[1]} - {user[2]:.1f} литр"
#                     for index, user in enumerate(top_users)
#                 ])
#             else:
#                 user_statistic = "Группада оюнчу жок"
#
#             # Отправляем сообщение с информацией о топ-10 пользователях
#             await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}", reply_markup=cancel_to_users_top)
#
#         if callback.data == "groups_day_top":
#             top_users = db.get_global_day_top_users()
#
#             # Формируем строку с перечислением пользователей
#             if top_users:
#                 user_statistic = "\n".join([
#                     f"{index + 1}. {user[1]} - {user[2]:.1f} литр"
#                     for index, user in enumerate(top_users)
#                 ])
#             else:
#                 user_statistic = "Группада оюнчу жок"
#
#             # Отправляем сообщение с информацией о топ-10 пользователях
#             await callback.message.edit_text(f"🥛🔝🥛Бир кундун ичинде глобалдуу эн мыкты оюнчулар:\n\n{user_statistic}",
#                                              reply_markup=cancel_to_group_top)
#
#         if callback.data == "groups_all_time_top":
#             top_groups = db.get_top_groups()
#
#             # Формируем строку с перечислением групп
#             if top_groups:
#                 group_statistic = "\n".join([
#                     f"{index + 1}.{group[1]} - {group[2]:.1f} литр"
#                     for index, group in enumerate(top_groups)
#                 ])
#             else:
#                 group_statistic = "Нет данных о группах."
#
#             # Отправляем сообщение с информацией о топ-группах
#             await callback.message.edit_text(f"🥛🔝🥛Глобалдуу эн кымызды коп ичкен группалар:\n\n{group_statistic}",
#                                              reply_markup=cancel_to_group_top)
#         if callback.data == "cancel":
#             await callback.message.edit_text(text="Сиз каалагн топту танданыз", reply_markup=stat_kb)
#     except Exception:
#         await callback.answer('Не так часто', show_alert=True)
#
