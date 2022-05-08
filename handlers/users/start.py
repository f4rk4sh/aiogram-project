from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from loader import dp
from keyboards.default import masters


@dp.message_handler(Command('start'))
async def command_start(message: Message):
    await message.answer('Glad to see you!\n'
                         'This bot belongs to Yarik and Dima shop \n'
                         'Please, check out our professional masters 👇 \n', reply_markup=masters)

