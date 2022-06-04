from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

# from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config

bot = Bot(token=config.TOKEN, parse_mode=types.ParseMode.HTML)

storage = RedisStorage2(
    host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB
)

# storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
