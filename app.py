from datetime import date, time

from aiogram import executor

from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.database import create_db
from utils.db_api.models import Master, Customer, Timeslot


async def on_startup(dispatcher):
    await create_db()
    await on_startup_notify(dispatcher)
    await set_default_commands(dispatcher)

    # uncomment to fulfill database

    # for i, name in enumerate(['james', 'mike', 'stephen']):
    #     await Master.create(chat_id=i+1,
    #                         name=name,
    #                         phone=str(i+1)*12,
    #                         info='some info')
    #     await Customer.create(chat_id=i+1,
    #                           name=name,
    #                           phone=str(i + 1) * 12)
    #     await Timeslot.create(date=date(2022, 5, 11),
    #                           time=time(10, 0, 0),
    #                           is_free=False, customer_id=i+1,
    #                           master_id=i+1)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
