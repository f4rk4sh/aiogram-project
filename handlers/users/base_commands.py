from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from data.config import ADMINS
from keyboards.default import kb_admin_commands, kb_master_commands, kb_masters
from loader import dp
from utils.db_api.models import Master


@dp.message_handler(Command('start'), state="*")
async def command_start(message: Message, state: FSMContext = None):
    if state is not None:
        await state.finish()
    text = f'Glad to see you, {message.from_user.full_name}!\n'\
           'Select one of the available commands 👇'
    if message.from_user.id in ADMINS:
        await message.answer(text=text, reply_markup=kb_admin_commands)
    elif await Master.query.where(Master.chat_id == message.from_user.id).gino.one_or_none():
        await message.answer(text=text, reply_markup=kb_master_commands)
    else:
        await message.answer('Glad to see you!\n'
                             'This bot belongs to Yarik and Dima shop \n'
                             'Please, check out our professional masters 👇 \n', reply_markup=kb_masters)


@dp.message_handler(text=['/menu', 'Back', 'Cancel'], state='*')
async def command_menu(message: Message, state: FSMContext = None):
    if state is not None:
        await state.finish()
    text = 'Main menu, choose one of the available commands 👇'
    if message.from_user.id in ADMINS:
        await message.answer(text=text, reply_markup=kb_admin_commands)
    elif await Master.query.where(Master.chat_id == message.from_user.id).gino.one_or_none():
        await message.answer(text=text, reply_markup=kb_master_commands)
    else:
        await message.answer(text=text, reply_markup=kb_masters)


@dp.message_handler(Command('help'), state='*')
async def command_help(message: Message, state: FSMContext = None):
    if state is not None:
        await state.finish()
    if message.from_user.id in ADMINS:
        await message.answer(text='<b>Available commands</b>\n\n'
                                  '<b>Send notifications:</b>\n\n'
                                  '/inform - <em>send notification to masters and/or customers</em>\n\n'
                                  '<b>Manage masters:</b>\n\n'
                                  '/add_master - <em>add new master</em>\n'
                                  '/delete_master - <em>delete existing master</em>\n\n'
                                  '<b>View statistics:</b>\n\n'
                                  '/statistic - <em>view statistic</em>',
                             reply_markup=kb_admin_commands)
    elif await Master.query.where(Master.chat_id == message.from_user.id).gino.one_or_none():
        await message.answer(text='<b>Available commands</b>\n\n'
                                  '<b>Profile managing:</b>\n\n'
                                  '/profile - <em>view personal profile</em>\n'
                                  '/update_info - <em>update profile info</em>\n'
                                  '/profile_photo - <em>upload profile photo</em>\n'
                                  '/portfolio_photo - <em>upload portfolio photo</em>\n\n'
                                  '<b>Timetable managing:</b>\n\n'
                                  '/timetable - <em>view timetable</em>',
                             reply_markup=kb_master_commands)
    else:
        await message.answer(text='<b>Available commands</b>\n\n'
                                  '/masters - <em>view list of masters</em>\n'
                                  '/visits - <em>view your upcoming or previous visits</em>\n'
                                  '/contact - <em>view contact information</em>',
                             reply_markup=kb_masters)
