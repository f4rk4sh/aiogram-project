from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from tortoise.expressions import Q

from data.config import ADMINS
from keyboards.default import kb_admin_commands, kb_master_commands, kb_masters
from loader import dp
from utils.db_api.models import Master


@dp.message_handler(Command("start"), state="*")
async def command_start(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    text = (
        f"Glad to see you, {message.from_user.full_name}!\n"
        "Select one of the available commands 👇"
    )
    if message.from_user.id in ADMINS:
        await message.answer(text=text, reply_markup=kb_admin_commands)
    elif await Master.filter(Q(chat_id=message.from_user.id) & Q(is_active=True)):
        await message.answer(text=text, reply_markup=kb_master_commands)
    else:
        await message.answer(
            "Glad to see you!\n"
            "This bot belongs to Yarik and Dima shop \n"
            "Please, check out our professional masters 👇 \n",
            reply_markup=kb_masters,
        )


@dp.message_handler(text=["/menu", "Back", "Cancel"], state="*")
async def command_menu(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    text = "Main menu, choose one of the available commands 👇"
    if message.from_user.id in ADMINS:
        await message.answer(text=text, reply_markup=kb_admin_commands)
    elif await Master.filter(Q(chat_id=message.from_user.id) & Q(is_active=True)):
        await message.answer(text=text, reply_markup=kb_master_commands)
    else:
        await message.answer(text=text, reply_markup=kb_masters)


@dp.message_handler(Command("help"), state="*")
async def command_help(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    if message.from_user.id in ADMINS:
        await message.answer(
            text="<b>Available commands</b>\n\n"
            "<b>Send notifications:</b>\n\n"
            "/inform - <em>send notification to masters and/or customers</em>\n\n"
            "<b>Manage masters:</b>\n\n"
            "/add_master - <em>add new master</em>\n"
            "/fire_master - <em>fire existing master</em>\n\n"
            "<b>View statistics:</b>\n\n"
            "/statistic - <em>view statistic</em>",
            reply_markup=kb_admin_commands,
        )
    elif await Master.filter(Q(chat_id=message.from_user.id) & Q(is_active=True)):
        await message.answer(
            text="<b>Available commands</b>\n\n"
            "<b>Profile managing:</b>\n\n"
            "/profile - <em>view personal profile</em>\n"
            "/update_info - <em>update profile info</em>\n"
            "/profile_photo - <em>upload profile photo</em>\n"
            "/portfolio_photo - <em>upload portfolio photo</em>\n\n"
            "<b>Timetable managing:</b>\n\n"
            "/timetable - <em>view timetable</em>",
            reply_markup=kb_master_commands,
        )
    else:
        await message.answer(
            text="<b>Available commands</b>\n\n"
            "/masters - <em>view list of masters, choose master, "
            "continue with portfolio browsing or with booking chosen master</em>\n\n"
            "/visits - <em>view your upcoming or previous visits, "
            "you can chose upcoming visit and cancel it if needed</em>\n\n"
            "/contact - <em>view contact information</em>",
            reply_markup=kb_masters,
        )
