from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

portfolio_photos_callback = CallbackData('Photo', 'page', 'master_id')


def get_portfolio_photos_keyboard(photos, page: int = 0):
    keyboard = InlineKeyboardMarkup(row_width=3)
    has_next_page = len(photos) > page + 1
    if page != 0:
        keyboard.add(
            InlineKeyboardButton(
                text='Previous photo',
                callback_data=portfolio_photos_callback.new(page=page - 1, master_id=photos[0].master_id)
            )
        )
    if has_next_page:
        keyboard.add(
            InlineKeyboardButton(
                text='Next photo',
                callback_data=portfolio_photos_callback.new(page=page + 1, master_id=photos[0].master_id)
            )
        )
    return keyboard
