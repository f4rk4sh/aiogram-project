from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_admin_commands = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Send notification"),
        ],
        [
            KeyboardButton(text="Manage masters"),
        ],
        [
            KeyboardButton(text="View statistic"),
        ],
    ],
    resize_keyboard=True,
)

kb_recipients = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Inform masters"),
        ],
        [
            KeyboardButton(text="Inform customers"),
        ],
        [
            KeyboardButton(text="Inform both masters and customers"),
        ],
    ],
    resize_keyboard=True,
)

kb_manage_masters = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Add master"),
        ],
        [
            KeyboardButton(text="Delete master"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
