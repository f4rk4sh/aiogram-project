from datetime import datetime, timedelta, date, time

from filters import get_dates, update_dates
from handlers.users.customer_commands import get_days_keyboard, date_span
from keyboards.default import kb_confirm_booking, kb_master_commands
from loader import dp
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from utils.db_api.models import Master, Timeslot, Customer
from states import MasterTimetable


@dp.message_handler(text=["My timetable", "/timetable"], state="*")
async def my_time_table(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    day = datetime.now().isoweekday()
    dates = get_dates(day)
    days_keyboard = get_days_keyboard(day, dates)
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await state.update_data(dates=dates, master_id=master.id)
    await MasterTimetable.waiting_for_choosing_day.set()
    await message.answer(f"Choose day",
                         reply_markup=days_keyboard)


@dp.callback_query_handler(text_contains="day", state=MasterTimetable.waiting_for_choosing_day)
async def book_day(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    chosen_date = call.data.split(' ')
    month = chosen_date[1].split('.')[1]
    day = chosen_date[1].split('.')[0]
    time_slot = InlineKeyboardMarkup()
    for time_inc in date_span(start=datetime(2022, int(month), int(day), 10),
                              end=datetime(2022, int(month), int(day), 19),
                              delta=timedelta(hours=1)):
        if await Timeslot.query.where((Timeslot.date == time_inc.date()) &
                                      (Timeslot.time == time_inc.time()) &
                                      (Timeslot.master_id == data['master_id'])).gino.one_or_none():
            time_slot.add(InlineKeyboardButton(text=f'❌ Since {time_inc.strftime("%H:%M")} ❌', callback_data="booked"))
        else:
            time_slot.add(InlineKeyboardButton(text=f'Since {time_inc.strftime("%H:%M")}', callback_data=time_inc.hour))

    await state.update_data(chosen_day=call.data.split(':')[1])
    await MasterTimetable.waiting_for_choosing_time.set()
    await call.message.answer(f"You are trying to view available slots "
                              f"on {call.data.split(':')[1]}",
                              reply_markup=time_slot)


@dp.callback_query_handler(text_contains="week", state=MasterTimetable.waiting_for_choosing_day)
async def book_day(call: CallbackQuery, state: FSMContext):
    cm = await state.get_data()
    dates = cm['dates']
    today = str(datetime.now().strftime("%d.%m"))
    first_day_in_dates = int(dates[0].split('.')[0])
    if call.data.split(':')[1] == "Previous week" and datetime.now() > datetime(year=datetime.now().year,
                                                                                month=int(dates[0].split('.')[1]),
                                                                                day=int(dates[0].split('.')[0])):
        await call.answer(text="You can't navigate to the past", show_alert=True)
    elif call.data.split(':')[1] == "Previous week":
        if int(today.split('.')[0]) + 7 > first_day_in_dates:
            day = datetime.now().isoweekday()
        else:
            day = 1
        new_dates = update_dates(text=call.data.split(':')[1], dates=dates)
        keyboard = get_days_keyboard(day, new_dates)
        await state.update_data(dates=new_dates)
        await call.message.edit_reply_markup(reply_markup=keyboard)
    else:
        day = 1
        new_dates = update_dates(text=call.data.split(':')[1], dates=dates)
        keyboard = get_days_keyboard(day, new_dates)
        await state.update_data(dates=new_dates)
        await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(state=MasterTimetable.waiting_for_choosing_time)
async def book_time(call: CallbackQuery, state: FSMContext):
    if call.data == "booked":
        await call.answer(text="The timeslot is already booked", show_alert=True)
    else:
        await call.answer(cache_time=1)
        data = await state.get_data()
        chosen_date = data['chosen_day'].split(' ')[1]
        chosen_time = call.data
        await state.update_data(selected_date=chosen_date, selected_time=int(chosen_time))
        await MasterTimetable.waiting_for_confirmation.set()
        await call.message.answer(f"You are trying to book this timeslot\n"
                                  f"Press the 'Confirm booking' button",
                                  reply_markup=kb_confirm_booking)


@dp.message_handler(text="Confirm booking", state=MasterTimetable.waiting_for_confirmation)
async def book_confirmation(message: Message, state: FSMContext):
    await message.answer(f"Please enter customers phone number without +380", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=MasterTimetable.waiting_for_confirmation)
async def phone_verification(message: Message, state: FSMContext):
    if len(message.text) != 9 or message.text.startswith(("+", "0")) or not message.text.isnumeric():
        await message.answer(f"Wrong number. Try again")
    else:
        data = await state.get_data()
        phone = '+380' + message.text
        chosen_date = date(year=datetime.now().year,
                           month=int(data['selected_date'].split('.')[1]),
                           day=int(data['selected_date'].split('.')[0]))
        chosen_time = time(hour=data['selected_time'],
                           minute=0,
                           second=0)
        await state.update_data(chosen_date=chosen_date, chosen_time=chosen_time)
        customer = await Customer.query.where(Customer.phone == phone).gino.one_or_none()

        if customer:
            await Timeslot.create(date=chosen_date,
                                  time=chosen_time,
                                  is_free=False,
                                  customer_id=customer.id,
                                  master_id=data['master_id'])
            await message.answer(f"Done!", reply_markup=kb_master_commands)
            await state.finish()
        else:

            await state.update_data(phone=phone)
            await MasterTimetable.waiting_for_new_customer_name.set()
            await message.answer('Please enter customers name', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=MasterTimetable.waiting_for_new_customer_name)
async def customer_name(message: Message, state:FSMContext):
    if message.text.startswith('/'):
        await MasterTimetable.waiting_for_new_customer_name.set()
        await message.answer("Command can't be a customers name")
    else:
        data = await state.get_data()
        customer = await Customer.create(name=message.text, phone=data['phone'])
        await Timeslot.create(date=data['chosen_date'],
                              time=data['chosen_time'],
                              is_free=False,
                              customer_id=customer.id, master_id=data['master_id'])
        await message.answer(f"Done!", reply_markup=kb_master_commands)
        await state.finish()
