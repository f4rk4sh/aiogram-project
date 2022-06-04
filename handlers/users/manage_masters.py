import logging
from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)
from aiogram.utils.exceptions import ChatNotFound
from tortoise.expressions import Q

from filters import IsAdmin
from keyboards.default import kb_admin_commands, kb_manage_masters
from keyboards.inline import kb_delete_confirm
from loader import bot, dp
from states import AddMaster, FireMaster
from utils.db_api.models import Customer, Master, Timeslot


@dp.message_handler(IsAdmin(), text="Manage masters")
async def manage_masters(message: Message):
    await message.answer("Select action", reply_markup=kb_manage_masters)


@dp.message_handler(IsAdmin(), text=["Add master", "/add_master"], state="*")
async def set_chat_id(message: Message, state: FSMContext):
    if state:
        await state.finish()
    await message.answer(
        "Enter master's telegram chat id\n\n" "<em>HINT: use only numbers</em>",
        reply_markup=ReplyKeyboardRemove(),
    )
    await AddMaster.chat_id.set()


@dp.message_handler(regexp=r"^\d+$", state=AddMaster.chat_id)
async def set_name(message: Message, state: FSMContext):
    master = await Master.get_or_none(chat_id=int(message.text))
    if master:
        master.is_active = True
        await master.save()
        await message.answer(
            "<b>Notification:</b>\n\n" "You have reinstate a fired employee",
            reply_markup=kb_admin_commands,
        )
        await state.finish()
    else:
        await state.update_data(chat_id=int(message.text))
        await message.answer(
            "Enter master's full name\n\n"
            "<em>HINT: need to contain firstname and lastname</em>"
        )
        await AddMaster.name.set()


@dp.message_handler(regexp=r"^\S+\s\S+$", state=AddMaster.name)
async def set_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Enter master's phone number\n\n"
        '<em>HINT: valid format "+380[phone number]"</em>'
    )
    await AddMaster.phone.set()


@dp.message_handler(regexp=r"\+380\d{9}", state=AddMaster.phone)
async def set_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "Enter master's info\n\n" "<em>HINT: up to 200 characters</em>"
    )
    await AddMaster.info.set()


@dp.message_handler(regexp=r"^[^\/].{1,200}$", state=AddMaster.info)
async def add_master(message: Message, state: FSMContext):
    data = await state.get_data()
    await Master.create(info=message.text, **data)
    await message.answer(
        "<b>Notification:</b>\n\n" "Master has been successfully added",
        reply_markup=kb_admin_commands,
    )
    await state.finish()


@dp.message_handler(IsAdmin(), text=["Fire the master", "/fire_master"], state="*")
async def select_master(message: Message, state: FSMContext):
    if state:
        await state.finish()
    masters = await Master.filter(is_active=True)
    if masters:
        kb_master_list = InlineKeyboardMarkup()
        for master in masters:
            kb_master_list.add(
                InlineKeyboardButton(text=master.name, callback_data=master.id)
            )
        await message.answer(
            "Select the master you want to fire", reply_markup=kb_master_list
        )
        await FireMaster.select.set()
    else:
        await message.answer(
            "Unfortunately, there are no masters added yet",
            reply_markup=kb_admin_commands,
        )
        await state.finish()


@dp.callback_query_handler(state=FireMaster.select)
async def check_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await state.update_data(master_pk=int(call.data))
    await call.message.answer(
        "Do you really want to fire this master?", reply_markup=kb_delete_confirm
    )
    await FireMaster.confirm.set()


@dp.callback_query_handler(text_contains="cancel", state=FireMaster.confirm)
async def cancel_master_deletion(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.answer("Select action", reply_markup=kb_manage_masters)
    await state.finish()


@dp.callback_query_handler(text_contains="confirm", state=FireMaster.confirm)
async def delete_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    data = await state.get_data()
    master = await Master.get(pk=data["master_pk"])
    master.is_active = False
    await master.save()
    visits = await Timeslot.filter(Q(master=master) & Q(datetime__gt=datetime.now()))
    customers_pks = set()
    for visit in visits:
        customers_pks.add(visit.customer.pk)
        await visit.delete()
    for customer_pk in customers_pks:
        customer = await Customer.get(id=customer_pk)
        try:
            await bot.send_message(
                chat_id=customer.chat_id,
                text="<b>Notification:</b>\n\n"
                f"The master {master.name} is no longer working in our salon.\n"
                "For this reason all your visits to this master were cancelled.\n"
                "Please choose another one and book him.\n\n"
                "We apologize for the inconvenience.",
            )
        except ChatNotFound:
            logging.info(f"ChatNotFound: chat id - {customer.chat_id}")
            await call.message.answer(
                "<b>Alert:</b>\n\n"
                "Notification about visits cancellation due to the dismissal of the "
                f"master has not been sent to <b>{customer.name}, "
                f"phone number: {customer.phone} </b> automatically."
            )
    await call.message.answer(
        "<b>Notification:</b>\n\n" "Master has been successfully fired.",
        reply_markup=kb_admin_commands,
    )
    await state.finish()
