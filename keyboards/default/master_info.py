from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

master_info = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Portfolio"),
        ],
        [
            KeyboardButton(text="Book master"),
        ],
    ],
    resize_keyboard=True
)
