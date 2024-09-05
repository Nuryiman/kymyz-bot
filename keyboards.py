from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,)

price_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="5 аракет - 10⭐️", callback_data='10stars'),
        ]
    ]
)