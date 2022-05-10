from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from loader import dp
from keyboards.default import masters, kb_admin_commands
from data.config import ADMINS, MASTERS
from utils.db_api.models import Master, Customer


@dp.message_handler(Command('start'))
async def command_start(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer(f'Glad to see you, {message.from_user.full_name}!\n'
                             'Select one of the available commands:', reply_markup=kb_admin_commands)
    # need to be from database
    elif message.from_user.id in MASTERS:
        await message.answer(f'Glad to see you, {message.from_user.full_name}!\n')
    else:
        await message.answer('Glad to see you!\n'
                             'This bot belongs to Yarik and Dima shop \n'
                             'Please, check out our professional masters 👇 \n', reply_markup=masters)
