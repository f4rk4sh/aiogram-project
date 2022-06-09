import logging

from aiogram import Dispatcher

from data.config import ADMINS
from data.messages import get_message


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(chat_id=admin, text=get_message("notify_admins"))
        except Exception as e:
            logging.exception(e)
