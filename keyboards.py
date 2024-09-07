from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,)

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
