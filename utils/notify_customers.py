import logging
from asyncio import sleep
import aioschedule
from aiogram.utils.exceptions import ChatNotFound

from data.config import ADMINS
from utils.db_api.models import Timeslot, Customer
from datetime import datetime, timedelta
from loader import bot


async def notify_customer():
    visits = await Timeslot.query.where(Timeslot.datetime > datetime.now()).gino.all()
    in_an_hour = datetime.now() + timedelta(hours=1)
    for visit in visits:
        if visit.datetime <= in_an_hour:
            customer = await Customer.query.where(Customer.id == visit.customer_id).gino.first()
            try:
                await bot.send_message(chat_id=customer.chat_id,
                                       text='<b>Reminder:</b>\n\n'
                                            'You have upcoming visit in half an hour\n\n'
                                            'We are looking forward to meeting you!')
                await sleep(0.3)
            except ChatNotFound:
                logging.info(f'ChatNotFound: chat id - {customer.chat_id}')
                for admin in ADMINS:
                    await bot.send_message(
                        chat_id=admin,
                        text='<b>Alert:</b>\n\n'
                             f'Reminder has not been sent to <b>{customer.name}</b>, '
                             f'phone number: <b>{customer.phone}</b>'
                    )
                    await sleep(0.3)


async def scheduler():
    aioschedule.every().hour.at(':30').do(notify_customer)
    while True:
        await aioschedule.run_pending()
        await sleep(1)
