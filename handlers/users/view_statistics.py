from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from loader import dp
from keyboards.inline import kb_statistics


@dp.message_handler(text=['View statistic', '/statistic'], state='*')
async def view_statistic(message: Message, state: FSMContext):
    await message.answer('Select required statistic', reply_markup=kb_statistics)
    if state is not None:
        await state.finish()
