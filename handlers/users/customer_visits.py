import logging
import os
from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import ChatNotFound
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

from data.messages import get_message
from keyboards.default import kb_cancel_visit, kb_masters, kb_previous_visits
from loader import bot, dp
from states import CancelVisit, CustomerVisits
from utils.db_api.models import Customer, Master, Timeslot

portfolio_photos_callback = CallbackData("Visit", "visit_pk", "master_pk")


@dp.message_handler(text=["My visits", "/visits"], state="*")
async def customer_visits(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    customer = await Customer.get_or_none(chat_id=message.from_user.id)
    if customer:
        visits = await Timeslot.filter(customer=customer)
        if visits:
            kb_visits = InlineKeyboardMarkup()
            for visit in visits:
                if visit.datetime.timestamp() > datetime.now().timestamp():
                    master = (
                        await Master.all()
                        .prefetch_related(
                            Prefetch("timeslots", queryset=Timeslot.filter(pk=visit.pk))
                        )
                        .first()
                    )
                    kb_visits.add(
                        InlineKeyboardButton(
                            text=f'Date: {visit.datetime.strftime("%d.%m")}, time: {visit.datetime.strftime("%H:%M")}',
                            callback_data=portfolio_photos_callback.new(
                                visit_pk=visit.pk, master_pk=master.pk
                            ),
                        )
                    )
            if kb_visits.inline_keyboard:
                await message.answer(
                    text=get_message("upcoming_visits"),
                    reply_markup=kb_visits,
                )
                await message.answer(
                    text=get_message("archive"), reply_markup=kb_previous_visits
                )
            else:
                await message.answer(
                    text=get_message("no_upcoming_visits").format(
                        get_message("archive")
                    ),
                    reply_markup=kb_previous_visits,
                )
            await state.update_data(customer_pk=customer.pk)
            await CustomerVisits.visits.set()
        else:
            await message.answer(text=get_message("no_visits"), reply_markup=kb_masters)
    else:
        await message.answer(text=get_message("no_visits"), reply_markup=kb_masters)


@dp.callback_query_handler(
    portfolio_photos_callback.filter(), state=CustomerVisits.visits
)
async def visit_detail(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    await call.answer(cache_time=1)
    visit = await Timeslot.get(pk=int(callback_data["visit_pk"]))
    master = await Master.get(pk=int(callback_data["master_pk"]))
    if master.photo_id:
        await call.message.answer_photo(
            photo=master.photo_id,
            caption=get_message("visit_detail").format(
                master.name,
                visit.datetime.strftime("%d.%m"),
                visit.datetime.strftime("%H:%M"),
                master.info,
            ),
            reply_markup=kb_cancel_visit,
        )
    else:
        await call.message.answer(
            text=get_message("visit_detail").format(
                master.name,
                visit.datetime.strftime("%d.%m"),
                visit.datetime.strftime("%H:%M"),
                master.info,
            ),
            reply_markup=kb_cancel_visit,
        )
    await state.update_data(
        visit_pk=visit.pk,
        master_chat_id=master.chat_id,
        master_name=master.name,
    )
    await CancelVisit.visit.set()


@dp.message_handler(text="Cancel visit", state=CancelVisit.visit)
async def visit_cancel(message: Message, state: FSMContext):
    data = await state.get_data()
    visit = await Timeslot.get(pk=data["visit_pk"])
    try:
        await bot.send_message(
            chat_id=data["master_chat_id"],
            text=get_message("visit_cancel_notification").format(
                visit.datetime.strftime("%d.%m"), visit.datetime.strftime("%H:%M")
            ),
        )
    except ChatNotFound:
        logging.info(f'ChatNotFound: chat id - {data["master_chat_id"]}')
        await message.answer(
            text=get_message("visit_cancel_no_master_chat_id_alert").format(
                data["master_name"], str(os.getenv("PHONE_NUM"))
            )
        )
    await visit.delete()
    await message.answer(
        text=get_message("visit_cancel_success"), reply_markup=kb_masters
    )
    await state.finish()


@dp.message_handler(text="Archive", state=CustomerVisits.visits)
async def archive_visits(message: Message, state: FSMContext):
    data = await state.get_data()
    customer = await Customer.get(pk=data["customer_pk"])
    visits = await Timeslot.filter(
        Q(customer=customer) & Q(datetime__lt=datetime.now())
    )
    text = get_message("previous_visits")
    if visits:
        for visit in visits:
            master = (
                await Master.all()
                .prefetch_related(
                    Prefetch("timeslots", queryset=Timeslot.filter(pk=visit.pk))
                )
                .first()
            )
            text += get_message("previous_visits_info").format(
                master.name,
                visit.datetime.strftime("%d.%m"),
                visit.datetime.strftime("%H:%M"),
            )
        await message.answer(text=text, reply_markup=kb_masters)
    else:
        await message.answer(
            text=get_message("no_previous_visits"),
            reply_markup=kb_masters,
        )
    await state.finish()
