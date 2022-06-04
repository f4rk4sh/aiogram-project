from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

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
