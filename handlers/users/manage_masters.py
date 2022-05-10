import re

from aiogram.dispatcher import FSMContext

from loader import dp
from utils.db_api.models import Master
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.default import kb_manage_masters, kb_admin_commands
from states.manage_masters import AddMaster


@dp.message_handler(text='Manage masters')
async def manage_masters(message: Message):
    await message.answer('Select action', reply_markup=kb_manage_masters)


@dp.message_handler(text='Add master')
async def set_chat_id(message: Message):
    await message.answer('Enter master\'s telegram chat id', reply_markup=ReplyKeyboardRemove())
    await AddMaster.chat_id.set()


@dp.message_handler(state=AddMaster.chat_id)
async def set_name(message: Message, state: FSMContext):
    try:
        await state.update_data(chat_id=int(message.text))
        await message.answer('Enter master\'s full name')
        await AddMaster.name.set()
    except ValueError:
        await message.answer('Enter master\'s telegram chat id in a correct format')
        await AddMaster.chat_id.set()


@dp.message_handler(state=AddMaster.name)
async def set_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Enter master\'s phone number')
    await AddMaster.phone.set()


@dp.message_handler(state=AddMaster.phone)
async def set_phone(message: Message, state: FSMContext):
    if re.findall(r'\+?\d{12}', message.text):
        await state.update_data(phone=message.text)
        await message.answer('Enter master\'s info')
        await AddMaster.info.set()
    else:
        await message.answer('Enter master\'s phone number in a correct format')
        await AddMaster.phone.set()


@dp.message_handler(state=AddMaster.info)
async def add_master(message: Message, state: FSMContext):
    data = await state.get_data()
    await Master.create(info=message.text, **data)
    await message.answer('Master has been successfully added', reply_markup=kb_admin_commands)
    await state.reset_state()


@dp.message_handler(text='List of masters')
async def master_list():
    masters = await Master.query.gino.all()
