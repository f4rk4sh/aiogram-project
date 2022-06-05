import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from data.messages import get_message
from keyboards.default import kb_back
from loader import dp


@dp.message_handler(text=["Contacts", "/contact"], state="*")
async def contact(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    await message.answer(
        text=get_message("contact_info").format(
            str(os.getenv("SALON_NAME")),
            str(os.getenv("LOCATION")),
            str(os.getenv("WORK_TIME")),
            str(os.getenv("PHONE_NUM")),
        ),
        reply_markup=kb_back,
    )
