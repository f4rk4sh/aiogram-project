from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_master_info = ReplyKeyboardMarkup(
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

kb_masters = ReplyKeyboardMarkup(
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

kb_confirm_booking = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Confirm booking"),
        ],
    ],
    resize_keyboard=True
)
