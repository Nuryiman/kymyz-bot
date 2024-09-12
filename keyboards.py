from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           ReplyKeyboardMarkup,
                           KeyboardButton)

price_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="5 аракет - 10⭐️", callback_data='10stars'),
        ],
        [
            InlineKeyboardButton(text="10 аракет - 20⭐️", callback_data='20stars'),
        ],
        [
            InlineKeyboardButton(text="15 аракет - 25⭐️", callback_data='25stars'),
        ],
    ]
)

stat_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Эн мыкты 10 оюнчу", callback_data='top_players')
        ],
        [
            InlineKeyboardButton(text="Эн мыкты 10 группа", callback_data='top_groups')
        ]
    ]
)

bot_username = "kymyz_slx_bot"

add_bot_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ботту группага кошуу", url=f'https://t.me/{bot_username}?startgroup=new')
        ]
    ]
)

# Создаем инлайн-кнопки
rek_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отправить", callback_data="send_ad"),
            InlineKeyboardButton(text="Заново", callback_data="retry_ad"),
        ],
        [
            InlineKeyboardButton(text="не отправлять", callback_data="not_send")
        ]
    ]
)

day_or_alltime_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Бугунку топ", callback_data="users_day_top")
        ],
        [
            InlineKeyboardButton(text="Бардык убакыт боюнча топ", callback_data="users_all_time_top")
        ],
        [
            InlineKeyboardButton(text="Артка", callback_data="cancel")
        ]
    ]
)

day_or_alltime_group_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Бугунку топ", callback_data="groups_day_top")
        ],
        [
            InlineKeyboardButton(text="Бардык убакыт боюнча топ", callback_data="groups_all_time_top")
        ],
        [
            InlineKeyboardButton(text="Артка", callback_data="cancel")
        ]
    ]
)

cancel_to_users_top = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Артка", callback_data="cancel_to_stat")
        ]
    ]
)

cancel_to_group_top = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Артка", callback_data="cancel_to_stat_group")
        ]
    ]
)


def rek_kb(text: str, url: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, url=url)
            ]
        ]
    )
    return markup


def all_reklams(*ads):
    buttons = [
        [KeyboardButton(text=item)] for item in ads
    ]

    markup = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите рекламу для удаления",
        selective=True
    )
    return markup


rm_reklam = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Удалить", callback_data="yes"),
            InlineKeyboardButton(text="Не удалять", callback_data="no")
        ]
    ]
)
