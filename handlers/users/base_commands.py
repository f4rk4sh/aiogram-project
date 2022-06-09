from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from tortoise.expressions import Q

from data.config import ADMINS
from data.messages import get_message
from keyboards.default.kb_admin import kb_admin_commands
from keyboards.default.kb_customer import kb_customer_commands
from keyboards.default.kb_master import kb_master_commands

from loader import dp
from utils.db_api.models import Master


@dp.message_handler(Command("start"), state="*")
async def command_start(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    if message.from_user.id in ADMINS:

        await message.answer(
            text=get_message("start").format(message.from_user.full_name),
            reply_markup=kb_admin_commands,
        )
    elif await Master.filter(Q(chat_id=message.from_user.id) & Q(is_active=True)):
        await message.answer(
            text=get_message("start").format(message.from_user.full_name),
            reply_markup=kb_master_commands,
        )
    else:
        await message.answer(
            text=get_message("start"),
            reply_markup=kb_customer_commands,
        )


@dp.message_handler(text=["/menu", "Back", "Cancel"], state="*")
async def command_menu(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    if message.from_user.id in ADMINS:
        await message.answer(text=get_message("menu"), reply_markup=kb_admin_commands)
    elif await Master.filter(Q(chat_id=message.from_user.id) & Q(is_active=True)):
        await message.answer(text=get_message("menu"), reply_markup=kb_master_commands)
    else:
        await message.answer(text=get_message("menu"), reply_markup=kb_customer_commands)


@dp.message_handler(Command("help"), state="*")
async def command_help(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    if message.from_user.id in ADMINS:
        await message.answer(
            text=get_message("help_admin"),
            reply_markup=kb_admin_commands,
        )
    elif await Master.filter(Q(chat_id=message.from_user.id) & Q(is_active=True)):
        await message.answer(
            text=get_message("help_master"),
            reply_markup=kb_master_commands,
        )
    else:
        await message.answer(
            text=get_message("help_customer"),
            reply_markup=kb_customer_commands,
        )
