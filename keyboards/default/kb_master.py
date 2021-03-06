from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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
            KeyboardButton(text="Upload portfolio photo"),
        ],
        [
            KeyboardButton(text="Upload profile photo"),
        ],
        [
            KeyboardButton(text="Update profile info"),
        ],
    ],
    resize_keyboard=True,
)

kb_master_cancel_booking = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Cancel booking"),
        ],
        [
            KeyboardButton(text="Back"),
        ],
    ],
    resize_keyboard=True,
)
