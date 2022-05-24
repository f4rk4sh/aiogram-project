import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keyboards.default import kb_back
from loader import dp


@dp.message_handler(text=['Contacts', '/contact'], state='*')
async def contact(message: Message, state: FSMContext = None):
    if state is not None:
        await state.finish()
    await message.answer(text=f'<b>{str(os.getenv("SALON_NAME"))}</b>\n\n'
                              f'📍 {str(os.getenv("LOCATION"))}\n\n'
                              f'🕑 {str(os.getenv("WORK_TIME"))}\n\n'
                              f'📞 {str(os.getenv("PHONE_NUM"))}',
                         reply_markup=kb_back)
