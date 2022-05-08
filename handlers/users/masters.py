import logging

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from loader import dp
from keyboards.inline import master_choice


@dp.message_handler(text="List of our masters")
async def list_of_masters(message: Message):
    await message.answer("Here are our best masters", reply_markup=master_choice)


@dp.callback_query_handler(text_contains='Master')
async def chosen_master(call: CallbackQuery):
    await call.answer(cache_time=10)
    logging.info(F"callback {call.data}")
    await call.message.answer(f"You have chosen {call.data.split(':')[1]}")
