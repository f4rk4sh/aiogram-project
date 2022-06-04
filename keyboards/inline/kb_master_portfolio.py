from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kb_portfolio_photo = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Add one more", callback_data="one_more"),
            InlineKeyboardButton(text="Main menu", callback_data="main_menu"),
        ]
    ],
)
