from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

masters = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="List of our masters"),
        ],
        [
            KeyboardButton(text="My visits"),
        ],
        [
            KeyboardButton(text="Contacts"),
        ],
    ],
    resize_keyboard=True
)
