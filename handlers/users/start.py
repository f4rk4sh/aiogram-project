from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from loader import dp


@dp.message_handler(Command('start'))
async def command_start(message: Message):
    await message.answer('Glad to see you!\n'
                         'Choose an action 👇')
