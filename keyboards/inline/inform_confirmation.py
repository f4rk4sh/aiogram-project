from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


kb_inform_confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Confirm', callback_data='confirm')
        ],
        [
            InlineKeyboardButton(text='Change', callback_data='change')
        ]
    ]
)
