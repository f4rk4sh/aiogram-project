from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
storage = MemoryStorage()
bot = Bot(token=config.TOKEN, parse_mode=types.ParseMode.HTML)

dp = Dispatcher(bot, storage=storage)
