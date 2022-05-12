from aiogram.types import Message
from loader import dp
from keyboards.inline import kb_statistics


@dp.message_handler(text=['View statistic', '/statistic'])
async def view_statistic(message: Message):
    await message.answer('Select required statistic', reply_markup=kb_statistics)
