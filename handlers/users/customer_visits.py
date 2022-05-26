from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import ChatNotFound

from keyboards.default import kb_cancel_visit, kb_masters, kb_previous_visits
from loader import bot, dp
from states import CancelVisit, CustomerVisits
from utils.db_api.models import Customer, Master, Timeslot

portfolio_photos_callback = CallbackData('Visit', 'visit_id', 'master_id')


@dp.message_handler(text=['My visits', '/visits'], state='*')
async def customer_visits(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    customer = await Customer.query.where(Customer.chat_id == message.from_user.id).gino.one_or_none()
    visits = await Timeslot.query.where(Timeslot.customer_id == customer.id).gino.all()
    if visits:
        kb_visits = InlineKeyboardMarkup()
        for visit in visits:
            if visit.datetime > datetime.now():
                master = await Master.query.where(Master.id == visit.master_id).gino.first()
                kb_visits.add(
                    InlineKeyboardButton(
                        text=f'Date: {visit.datetime.strftime("%d.%m")}, time: {visit.datetime.strftime("%H:%M")}',
                        callback_data=portfolio_photos_callback.new(
                            visit_id=visit.id,
                            master_id=master.id
                        )
                    )
                )
        text = 'Press <b>"Archive"</b> to view previous visits\n\n' \
               'Press <b>"Back"</b> to main menu'
        if kb_visits.inline_keyboard:
            await message.answer(
                text='<b>Upcoming visits:</b>\n\n'
                     '<em>HINT: if you want to view details or cancel upcoming visit, click on needed one</em>',
                reply_markup=kb_visits)
            await message.answer(text=text, reply_markup=kb_previous_visits)
        else:
            await message.answer(text=f'Unfortunately, you have no upcoming visits\n\n{text}',
                                 reply_markup=kb_previous_visits)
        await state.update_data(customer_id=customer.id)
        await CustomerVisits.visits.set()
    else:
        await message.answer(text='Unfortunately, you have no visits yet', reply_markup=kb_masters)


@dp.callback_query_handler(portfolio_photos_callback.filter(), state=CustomerVisits.visits)
async def visit_detail(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    await call.answer(cache_time=1)
    visit = await Timeslot.query.where(Timeslot.id == int(callback_data['visit_id'])).gino.first()
    master = await Master.query.where(Master.id == visit.master_id).gino.first()
    text = f'<b>Master:</b> {master.name}\n'\
           f'<b>Date:</b> {visit.datetime.strftime("%d.%m")}\n'\
           f'<b>Time:</b> {visit.datetime.strftime("%H:%M")}\n' \
           f'<b>Master info:</b> {master.info}'

    if master.photo_id:
        await call.message.answer_photo(photo=master.photo_id, caption=text, reply_markup=kb_cancel_visit)
    else:
        await call.message.answer(text=text, reply_markup=kb_cancel_visit)
    await state.update_data(visit_id=visit.id, master_chat_id=master.chat_id)
    await CancelVisit.visit.set()


@dp.message_handler(text='Cancel visit', state=CancelVisit.visit)
async def visit_cancel(message: Message, state: FSMContext):
    data = await state.get_data()
    visit = await Timeslot.query.where(Timeslot.id == data['visit_id']).gino.first()
    try:
        await bot.send_message(chat_id=data['master_chat_id'],
                               text='<b>Notification:</b>\n\n'
                                    'Customer has been canceled his visit\n\n'
                                    f'Timeslot <b>{visit.datetime.strftime("%d.%m")}, {visit.datetime.strftime("%H:%M")}</b> is now free')
    except ChatNotFound:
        await message.answer("Master is unreachable")

    await visit.delete()
    await message.answer('Visit has been successfully canceled', reply_markup=kb_masters)
    await state.finish()


@dp.message_handler(text='Archive', state=CustomerVisits.visits)
async def archive_visits(message: Message, state: FSMContext):
    data = await state.get_data()
    visits = await Timeslot.query.where(
        (Timeslot.customer_id == data['customer_id']) &
        (Timeslot.datetime < datetime.now())
    ).gino.all()
    text = '<b>Previous visits:</b>'
    if visits:
        for visit in visits:
            master = await Master.query.where(Master.id == visit.master_id).gino.one_or_none()
            text += f'\n\n<b>Master:</b> {master.name}\n' \
                    f'<b>Date:</b> {visit.datetime("%d.%m")}\n' \
                    f'<b>Time:</b> {visit.datetime.strftime("%H:%M")}'

        await message.answer(text=text, reply_markup=kb_masters)
    else:
        await message.answer(text='Unfortunately, you have no  previous visits yet', reply_markup=kb_masters)
    await state.finish()
