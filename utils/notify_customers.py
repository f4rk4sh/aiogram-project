import logging
from asyncio import sleep
from datetime import datetime, timedelta

import aioschedule
from aiogram.utils.exceptions import ChatNotFound

from data.config import ADMINS
from data.messages import get_message
from loader import bot
from utils.db_api.models import Timeslot


async def notify_customer():
    visits = await Timeslot.filter(datetime__gt=datetime.now())
    in_an_hour = datetime.now() + timedelta(hours=1)
    for visit in visits:
        if visit.datetime.timestamp() <= in_an_hour.timestamp():
            try:
                await bot.send_message(
                    chat_id=visit.customer.chat_id,
                    text=get_message("customer_reminder"),
                )
                await sleep(0.3)
            except ChatNotFound:
                logging.info(f"ChatNotFound: chat id - {visit.customer.chat_id}")
                for admin in ADMINS:
                    await bot.send_message(
                        chat_id=admin,
                        text=get_message("reminder_no_chat_id_alert").format(
                            visit.customer.name, visit.customer.phone
                        ),
                    )
                    await sleep(0.3)


async def scheduler():
    aioschedule.every().hour.at(":30").do(notify_customer)
    while True:
        await aioschedule.run_pending()
        await sleep(1)
