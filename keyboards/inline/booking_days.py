from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

master_callback = CallbackData("booking_days", "day_of_week")
switching = CallbackData("switch", "switch_to")

booking_days = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Monday", callback_data=master_callback.new(day_of_week="Monday"))
        ],
        [
            InlineKeyboardButton(text="Tuesday", callback_data=master_callback.new(day_of_week="Tuesday"))
        ],
        [
            InlineKeyboardButton(text="Wednesday", callback_data=master_callback.new(day_of_week="Wednesday"))
        ],
        [
            InlineKeyboardButton(text="Thursday", callback_data=master_callback.new(day_of_week="Thursday"))
        ],
        [
            InlineKeyboardButton(text="Friday", callback_data=master_callback.new(day_of_week="Friday"))
        ],
        [
            InlineKeyboardButton(text="Saturday", callback_data=master_callback.new(day_of_week="Saturday"))
        ],
        [
            InlineKeyboardButton(text="Sunday", callback_data=master_callback.new(day_of_week="Sunday"))
        ],
        [
            InlineKeyboardButton(text="Previous week", callback_data=switching.new(switch_to="Previous week")),
            InlineKeyboardButton(text="Next week", callback_data=switching.new(switch_to="Next week"))
        ],
    ]
)
