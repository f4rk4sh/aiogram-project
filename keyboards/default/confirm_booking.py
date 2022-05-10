from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

confirm_booking = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Confirm booking"),
        ],
    ],
    resize_keyboard=True
)
