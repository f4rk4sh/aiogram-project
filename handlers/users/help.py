from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from loader import dp


@dp.message_handler(Command('help'))
async def command_help(message: Message):
    await message.answer(f'hello {message.from_user.full_name}!\n'
                         f'ID: {message.from_user.id}')
