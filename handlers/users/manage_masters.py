from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, ReplyKeyboardRemove)

from filters import IsAdmin
from keyboards.default import kb_admin_commands, kb_manage_masters
from keyboards.inline import kb_delete_confirm
from loader import dp
from states import AddMaster, DeleteMaster
from utils.db_api.models import Master


@dp.message_handler(IsAdmin(), text='Manage masters')
async def manage_masters(message: Message):
    await message.answer('Select action', reply_markup=kb_manage_masters)


@dp.message_handler(IsAdmin(), text=['Add master', '/add_master'], state='*')
async def set_chat_id(message: Message, state: FSMContext):
    if state is not None:
        await state.finish()
    await message.answer('Enter master\'s telegram chat id\n\n'
                         '<em>HINT: use only numbers</em>', reply_markup=ReplyKeyboardRemove())
    await AddMaster.chat_id.set()


@dp.message_handler(regexp=r'^\d+$', state=AddMaster.chat_id)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(chat_id=int(message.text))
    await message.answer('Enter master\'s full name\n\n'
                         '<em>HINT: need to contain firstname and lastname</em>')
    await AddMaster.name.set()


@dp.message_handler(regexp=r'^\S+\s\S+$', state=AddMaster.name)
async def set_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Enter master\'s phone number\n\n'
                         '<em>HINT: valid format "+380[phone number]"</em>')
    await AddMaster.phone.set()


@dp.message_handler(regexp=r'\+380\d{9}', state=AddMaster.phone)
async def set_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer('Enter master\'s info\n\n'
                         '<em>HINT: up to 200 characters</em>')
    await AddMaster.info.set()


@dp.message_handler(regexp=r'^[^\/].{1,200}$', state=AddMaster.info)
async def add_master(message: Message, state: FSMContext):
    data = await state.get_data()
    await Master.create(info=message.text, **data)
    await message.answer('Master has been successfully added', reply_markup=kb_admin_commands)
    await state.finish()


@dp.message_handler(IsAdmin(), text=['Delete master', '/delete_master'], state='*')
async def select_master(message: Message, state: FSMContext):
    if state is not None:
        await state.finish()
    masters = await Master.query.gino.all()
    kb_master_list = InlineKeyboardMarkup()
    for master in masters:
        kb_master_list.add(InlineKeyboardButton(text=master.name, callback_data=master.id))
    await message.answer('Select master for deletion', reply_markup=kb_master_list)
    await DeleteMaster.select.set()


@dp.callback_query_handler(state=DeleteMaster.select)
async def check_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await state.update_data(master_id=int(call.data))
    await call.message.answer('Do you really want to delete this master?', reply_markup=kb_delete_confirm)
    await DeleteMaster.confirm.set()


@dp.callback_query_handler(text_contains='cancel', state=DeleteMaster.confirm)
async def cancel_master_deletion(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.answer('Select action', reply_markup=kb_manage_masters)
    await state.finish()


@dp.callback_query_handler(text_contains='confirm', state=DeleteMaster.confirm)
async def delete_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    data = await state.get_data()
    master = await Master.query.where(Master.id == data.get('master_id')).gino.first()
    await master.delete()
    await call.message.answer('Master has been successfully deleted', reply_markup=kb_admin_commands)
    await state.finish()
