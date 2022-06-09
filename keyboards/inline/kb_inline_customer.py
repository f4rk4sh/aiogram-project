from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

master_callback = CallbackData("booking_slot", "time_slot")

kb_time_slots = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="10:00am - 11:00am",
                callback_data=master_callback.new(time_slot="since_10am"),
            )
        ],
        [
            InlineKeyboardButton(
                text="11:00am - 12:00am",
                callback_data=master_callback.new(time_slot="since_11am"),
            )
        ],
        [
            InlineKeyboardButton(
                text="12:00am - 1:00pm",
                callback_data=master_callback.new(time_slot="since_12am"),
            )
        ],
        [
            InlineKeyboardButton(
                text="1:00pm - 2:00pm",
                callback_data=master_callback.new(time_slot="since_1pm"),
            )
        ],
        [
            InlineKeyboardButton(
                text="2:00pm - 3:00pm",
                callback_data=master_callback.new(time_slot="since_2pm"),
            )
        ],
        [
            InlineKeyboardButton(
                text="3:00pm - 4:00pm",
                callback_data=master_callback.new(time_slot="since_3pm"),
            )
        ],
        [
            InlineKeyboardButton(
                text="4:00pm - 5:00pm",
                callback_data=master_callback.new(time_slot="since_4pm"),
            )
        ],
        [
            InlineKeyboardButton(
                text="5:00pm - 6:00pm",
                callback_data=master_callback.new(time_slot="since_5pm"),
            )
        ],
        [
            InlineKeyboardButton(
                text="6:00pm - 7:00pm",
                callback_data=master_callback.new(time_slot="since_6pm"),
            )
        ],
        [
            InlineKeyboardButton(
                text="7:00pm - 8:00pm",
                callback_data=master_callback.new(time_slot="since_7pm"),
            )
        ],
    ]
)

portfolio_photos_callback = CallbackData("Photo", "page", "master_pk")


def get_portfolio_photos_keyboard(photos, master, page: int = 0):
    keyboard = InlineKeyboardMarkup(row_width=3)
    has_next_page = len(photos) > page + 1
    if page != 0:
        keyboard.add(
            InlineKeyboardButton(
                text="Previous photo",
                callback_data=portfolio_photos_callback.new(
                    page=page - 1, master_pk=master.pk
                ),
            )
        )
    if has_next_page:
        keyboard.add(
            InlineKeyboardButton(
                text="Next photo",
                callback_data=portfolio_photos_callback.new(
                    page=page + 1, master_pk=master.pk
                ),
            )
        )
    return keyboard
