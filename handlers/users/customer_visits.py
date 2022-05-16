from datetime import datetime


from aiogram.types import Message

from keyboards.default import kb_masters
from loader import dp
from utils.db_api.models import Timeslot, Master, Customer


@dp.message_handler(text=['My visits', '/visits'])
async def customer_visits(message: Message):
    customer = await Customer.query.where(Customer.chat_id == message.from_user.id).gino.one_or_none()
    if customer:
        visits = await Timeslot.query.where(Timeslot.customer_id == customer.id).gino.all()
        upcoming_visits = '<b>Upcoming visits:</b>'
        previous_visits = '<b>Previous visits:</b>'
        for visit in visits:
            master = await Master.query.where(Master.id == visit.master_id).gino.one_or_none()
            text = f'\n\n<b>Master:</b> {master.name}\n' \
                   f'<b>Date:</b> {visit.date}\n' \
                   f'<b>Time:</b> {visit.time}'
            if datetime.combine(visit.date, visit.time) < datetime.now():
                previous_visits += text
            elif datetime.combine(visit.date, visit.time) > datetime.now():
                upcoming_visits += text
        text = ''
        if len(upcoming_visits) > 23 and len(previous_visits) > 23:
            text += upcoming_visits + '\n\n' + previous_visits
        elif len(upcoming_visits) > 23:
            text += upcoming_visits
        elif len(previous_visits) > 23:
            text += previous_visits
        await message.answer(text=text, reply_markup=kb_masters)
    else:
        await message.answer(text='No visits yet\n'
                                  'Press "List of masters" to choose master',
                             reply_markup=kb_masters)
