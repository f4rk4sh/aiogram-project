from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb_master_info = ReplyKeyboardMarkup(
    one_time_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Book master"),
        ],
        [
            KeyboardButton(text="Portfolio"),
        ],
        [
            KeyboardButton(text="Back"),
        ],
    ],
    resize_keyboard=True,
)

kb_masters = ReplyKeyboardMarkup(
    one_time_keyboard=True,
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
    resize_keyboard=True,
)

kb_confirm_booking = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Confirm booking"),
        ],
        [KeyboardButton(text="Cancel")],
    ],
    resize_keyboard=True,
)

kb_request_contact = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Send contact", request_contact=True)],
        [KeyboardButton(text="Cancel")],
    ],
    resize_keyboard=True,
)

kb_previous_visits = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Archive")],
        [KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
)

kb_cancel_visit = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Cancel visit")],
        [KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
)

kb_back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Back")],
    ],
    resize_keyboard=True,
)
