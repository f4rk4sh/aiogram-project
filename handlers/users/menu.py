from aiogram.types import Message
from aiogram.dispatcher.filters import Command

from keyboards.default import kb_menu
from loader import dp


@dp.message_handler(Command('menu'))
async def menu(message: Message):
    await message.answer('Choose number from above', reply_markup=kb_menu)



