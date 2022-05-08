from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

master_callback = CallbackData("choose_master", "master_name")

master_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Master #1", callback_data=master_callback.new(master_name="Master #1"))
        ],
        [
            InlineKeyboardButton(text="Master #2", callback_data=master_callback.new(master_name="Master #2"))
        ],
        [
            InlineKeyboardButton(text="Master #3", callback_data=master_callback.new(master_name="Master #3"))
        ],
    ]
)
