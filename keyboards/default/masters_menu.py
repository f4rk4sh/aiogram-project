from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

masters = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="List of our masters"),
        ],
    ],
    resize_keyboard=True
)
