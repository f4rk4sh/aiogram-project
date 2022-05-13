import re

from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, ReplyKeyboardRemove)

from keyboards.default import kb_admin_commands, kb_manage_masters
from keyboards.inline import kb_delete_confirm
from loader import dp
from states import AddMaster, DeleteMaster
from utils.db_api.models import Master


@dp.message_handler(text='Manage masters')
async def manage_masters(message: Message):
    await message.answer('Select action', reply_markup=kb_manage_masters)


@dp.message_handler(text=['Add master', '/add_master'], state='*')
async def set_chat_id(message: Message, state: FSMContext):
    await message.answer('Enter master\'s telegram chat id', reply_markup=ReplyKeyboardRemove())
    if state is not None:
        await state.finish()
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
    if message.text.startswith('/'):
        await message.answer('You can not use command as the text of your profile info\n'
                             'Re-enter the text of the info')
        await AddMaster.name.set()
    else:
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
    if message.text.startswith('/'):
        await message.answer('You can not use command as the text of your profile info\n'
                             'Re-enter the text of the info')
        await AddMaster.info.set()
    else:
        data = await state.get_data()
        await Master.create(info=message.text, **data)
        await message.answer('Master has been successfully added', reply_markup=kb_admin_commands)
        await state.reset_state()


@dp.message_handler(text=['Delete master', '/delete_master'], state='*')
async def select_master(message: Message, state: FSMContext):
    masters = await Master.query.gino.all()
    kb_master_list = InlineKeyboardMarkup()
    for master in masters:
        kb_master_list.add(InlineKeyboardButton(text=master.name, callback_data=master.id))
    await message.answer('Select master for deletion', reply_markup=kb_master_list)
    if state is not None:
        await state.finish()
    await DeleteMaster.select.set()


@dp.callback_query_handler(state=DeleteMaster.select)
async def check_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    await state.update_data(master_id=int(call.data))
    await call.message.answer('Do you really want to delete this master?', reply_markup=kb_delete_confirm)
    await DeleteMaster.confirm.set()


@dp.callback_query_handler(text_contains='cancel', state=DeleteMaster.confirm)
async def cancel_master_deletion(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    await call.message.answer('Select action', reply_markup=kb_manage_masters)
    await state.finish()


@dp.callback_query_handler(text_contains='confirm', state=DeleteMaster.confirm)
async def delete_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    master = await Master.query.where(Master.id == data.get('master_id')).gino.first()
    await master.delete()
    await call.message.answer('Master has been successfully deleted', reply_markup=kb_admin_commands)
    await state.finish()
