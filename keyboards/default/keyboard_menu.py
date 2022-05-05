from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# test keyboard

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='10'),
            KeyboardButton(text='10')
        ],
        [
            KeyboardButton(text='100')
        ],
        [
            KeyboardButton(text='text1'),
            KeyboardButton(text='text2'),
            KeyboardButton(text='text3')
        ]
    ],
    resize_keyboard=True
)
