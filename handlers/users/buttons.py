from aiogram import types
from loader import dp


# handler to test keyboard


@dp.message_handler(text='10')
async def buttons_test(message: types.Message):
    await message.answer(f'hello {message.from_user.full_name}! \n'
                         f'your have chosen {message.text}')
