import asyncio

from aiogram import executor

import middlewares, filters, handlers
from loader import dp
from utils.db_api.models import init_db
from utils.notify_admins import on_startup_notify
from utils.notify_customers import scheduler
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await init_db()
    await on_startup_notify(dispatcher)
    await set_default_commands(dispatcher)
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
