from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from filters import IsAdmin
from keyboards.inline.kb_inline_admin import kb_statistics
from loader import dp


@dp.message_handler(IsAdmin(), text=["View statistic", "/statistic"], state="*")
async def view_statistic(message: Message, state: FSMContext):
    await message.answer("Select required statistic", reply_markup=kb_statistics)
    if state:
        await state.finish()
