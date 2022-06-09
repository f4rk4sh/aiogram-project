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

from data.messages import get_message
from filters import IsAdmin
from keyboards.default.kb_admin import kb_manage_masters, kb_admin_commands
from keyboards.inline.kb_inline_admin import kb_delete_confirm
from loader import bot, dp
from states.admin_states import AddMaster, FireMaster
from utils.db_api.models import Customer, Master, Timeslot


@dp.message_handler(IsAdmin(), text="Manage masters")
async def manage_masters(message: Message):
    await message.answer(
        text=get_message("select_action"), reply_markup=kb_manage_masters
    )


@dp.message_handler(IsAdmin(), text=["Add master", "/add_master"], state="*")
async def set_chat_id(message: Message, state: FSMContext):
    if state:
        await state.finish()
    await message.answer(
        text=get_message("set_chat_id"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await AddMaster.chat_id_typed.set()


@dp.message_handler(regexp=r"^\d+$", state=AddMaster.chat_id_typed)
async def set_name(message: Message, state: FSMContext):
    master = await Master.get_or_none(chat_id=int(message.text))
    if master:
        master.is_active = True
        await master.save()
        await message.answer(
            get_message("reinstate"),
            reply_markup=kb_admin_commands,
        )
        await state.finish()
    else:
        await state.update_data(chat_id=int(message.text))
        await message.answer(text=get_message("set_name"))
        await AddMaster.name_typed.set()


@dp.message_handler(regexp=r"^\S+\s\S+$", state=AddMaster.name_typed)
async def set_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text=get_message("set_phone"))
    await AddMaster.phone_typed.set()


@dp.message_handler(regexp=r"\+380\d{9}", state=AddMaster.phone_typed)
async def set_info(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(text=get_message("set_info"))
    await AddMaster.info_typed.set()


@dp.message_handler(regexp=r"^[^\/].{1,200}$", state=AddMaster.info_typed)
async def add_master(message: Message, state: FSMContext):
    data = await state.get_data()
    await Master.create(info=message.text, **data)
    await message.answer(
        text=get_message("add_master_success"),
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
            text=get_message("select_master"), reply_markup=kb_master_list
        )
        await FireMaster.master_selected.set()
    else:
        await message.answer(
            text=get_message("alert_no_master"),
            reply_markup=kb_admin_commands,
        )
        await state.finish()


@dp.callback_query_handler(state=FireMaster.master_selected)
async def check_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await state.update_data(master_pk=int(call.data))
    await call.message.answer(
        text=get_message("fire_confirm"), reply_markup=kb_delete_confirm
    )
    await FireMaster.confirm_selected.set()


@dp.callback_query_handler(text_contains="cancel", state=FireMaster.confirm_selected)
async def cancel_master_deletion(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.answer(
        get_message("select_action"), reply_markup=kb_manage_masters
    )
    await state.finish()


@dp.callback_query_handler(text_contains="confirm", state=FireMaster.confirm_selected)
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
                text=get_message("fire_notify_customer").format(master.name),
            )
        except ChatNotFound:
            logging.info(f"ChatNotFound: chat id - {customer.chat_id}")
            await call.message.answer(
                text=get_message("alert_fire_no_master_chat_id").format(
                    customer.name, customer.phone
                )
            )
    await call.message.answer(
        text=get_message("fire_master_success"),
        reply_markup=kb_admin_commands,
    )
    await state.finish()
