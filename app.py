import asyncio

from aiogram import executor

import middlewares, filters, handlers
from loader import dp
from utils import on_startup_notify, scheduler, set_default_commands
from utils.db_api.models import init_db


async def on_startup(dispatcher):
    await init_db()
    await on_startup_notify(dispatcher)
    await set_default_commands(dispatcher)
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
