from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_master_commands = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="My timetable"),
        ],
        [
            KeyboardButton(text="My profile"),
        ],
    ],
    resize_keyboard=True,
)

kb_master_profile = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Update profile info"),
        ],
        [
            KeyboardButton(text="Upload profile photo"),
        ],
    ],
    resize_keyboard=True,
)
