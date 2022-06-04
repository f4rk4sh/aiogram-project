from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kb_inform_confirm = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Confirm", callback_data="confirm"),
            InlineKeyboardButton(text="Change", callback_data="change"),
        ]
    ],
)

kb_delete_confirm = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Confirm", callback_data="confirm"),
            InlineKeyboardButton(text="Cancel", callback_data="cancel"),
        ]
    ],
)
