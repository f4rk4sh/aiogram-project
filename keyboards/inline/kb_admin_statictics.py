from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


kb_statistics = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Clients per week', callback_data='clients')
        ],
        [
            InlineKeyboardButton(text='New clients per week', callback_data='new_clients')
        ],
        [
            InlineKeyboardButton(text='Most popular master per week', callback_data='popular_master')
        ]
    ]
)
