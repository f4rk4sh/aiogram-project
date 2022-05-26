from asyncio import sleep
from datetime import datetime, timedelta, date, time

from asyncpg import UniqueViolationError

from filters import IsMaster
from keyboards.default import kb_confirm_booking, kb_master_commands, kb_master_cancel_booking
from loader import dp, bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from utils.db_api.models import Master, Timeslot, Customer
from states import MasterTimetable
from utils.misc import date_span


@dp.message_handler(IsMaster(), text=["My timetable", "/timetable"], state="*")
async def my_time_table(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    day = datetime.now().isoweekday()
    keyboard = InlineKeyboardMarkup()
    num_d = 7 - day
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    async for time_inc in date_span(start=datetime.now(),
                                    end=datetime.now() + timedelta(days=num_d),
                                    delta=timedelta(days=1)):
        if await Timeslot.query.where((Timeslot.date == time_inc.date()) & (Timeslot.master_id == master.id)).gino.one_or_none():
            keyboard.add(InlineKeyboardButton(text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                                              callback_data=f'busy'))
        else:
            keyboard.add(InlineKeyboardButton(text=f'{time_inc.strftime("%A %d.%m")}',
                                              callback_data=f'{time_inc.strftime("%A %d.%m")}'))
    keyboard.add(InlineKeyboardButton(text="Previous week", callback_data='Previous week'),
                 InlineKeyboardButton(text="Next week", callback_data='Next week'))
    await state.update_data(dima_last_day=datetime.now() + timedelta(days=num_d))
    await state.update_data(master_id=master.id)
    await MasterTimetable.waiting_for_choosing_day.set()
    await message.answer(f"Choose day",
                         reply_markup=keyboard)


@dp.callback_query_handler(text_contains="day", state=MasterTimetable.waiting_for_choosing_day)
async def book_day(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    chosen_date = call.data.split(' ')
    month = chosen_date[1].split('.')[1]
    day = chosen_date[1].split('.')[0]
    time_slot = InlineKeyboardMarkup()
    async for time_inc in date_span(start=datetime(2022, int(month), int(day), 10),
                                    end=datetime(2022, int(month), int(day), 19),
                                    delta=timedelta(hours=1)):
        if time_inc > datetime.now():
            if await Timeslot.query.where((Timeslot.datetime == time_inc) &
                                          (Timeslot.master_id == data['master_id'])).gino.one_or_none():
                time_slot.add(InlineKeyboardButton(text=f'❌ Since {time_inc.strftime("%H:%M")} ❌',
                                                   callback_data=f'booked_{time_inc.strftime("%y-%m-%d %H:%M:%S")}'))
            else:
                time_slot.add(InlineKeyboardButton(text=f'Since {time_inc.strftime("%H:%M")}',
                                                   callback_data=time_inc.hour))
    time_slot.add(InlineKeyboardButton(text=f'Make day off',
                                       callback_data='off'))
    await state.update_data(chosen_day=call.data, day_off=date(year=2022, month=int(month), day=int(day)))
    await MasterTimetable.waiting_for_choosing_time.set()
    await call.message.answer(f"Here is your schedule on <b>{call.data}</b>",
                              reply_markup=time_slot)


@dp.callback_query_handler(text_contains="week", state=MasterTimetable.waiting_for_choosing_day)
async def book_day(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if call.data == "Previous week":
        keyboard = InlineKeyboardMarkup()
        async for time_inc in date_span(start=data['dima_first_day'] - timedelta(days=6),
                                        end=data['dima_first_day'],
                                        delta=timedelta(days=1)):
            if await Timeslot.query.where(
                    (Timeslot.date == time_inc.date()) & (Timeslot.master_id == data['master_id'])).gino.one_or_none():
                keyboard.add(InlineKeyboardButton(text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                                                  callback_data=f'busy'))
            else:
                keyboard.add(InlineKeyboardButton(text=f'{time_inc.strftime("%A %d.%m")}',
                                                  callback_data=f'{time_inc.strftime("%A %d.%m")}'))
        keyboard.add(InlineKeyboardButton(text="Previous week", callback_data='Previous week'),
                     InlineKeyboardButton(text="Next week", callback_data='Next week'))
        await state.update_data(dima_first_day=data['dima_first_day'] - timedelta(days=7),
                                dima_last_day=data['dima_first_day'])
        await call.message.edit_reply_markup(reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup()
        async for time_inc in date_span(start=data['dima_last_day'] + timedelta(days=1),
                                        end=data['dima_last_day'] + timedelta(days=7),
                                        delta=timedelta(days=1)):
            if await Timeslot.query.where(
                    (Timeslot.date == time_inc.date()) & (Timeslot.master_id == data['master_id'])).gino.one_or_none():
                keyboard.add(InlineKeyboardButton(text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                                                  callback_data=f'busy'))
            else:
                keyboard.add(InlineKeyboardButton(text=f'{time_inc.strftime("%A %d.%m")}',
                                                  callback_data=f'{time_inc.strftime("%A %d.%m")}'))
        keyboard.add(InlineKeyboardButton(text="Previous week", callback_data='Previous week'),
                     InlineKeyboardButton(text="Next week", callback_data='Next week'))
        await state.update_data(dima_first_day=data['dima_last_day'],
                                dima_last_day=data['dima_last_day'] + timedelta(days=7))
        await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(text_contains="busy", state=MasterTimetable.waiting_for_choosing_day)
async def make_day_off(call: CallbackQuery, state: FSMContext):
    await call.answer(text="This is your day off. Enjoy!", show_alert=True)


@dp.callback_query_handler(text_contains="off", state=MasterTimetable.waiting_for_choosing_time)
async def make_day_off(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await Timeslot.create(master_id=data['master_id'], is_free=False, date=data['day_off'])
    await call.message.answer("Done", reply_markup=kb_master_commands)


@dp.callback_query_handler(state=MasterTimetable.waiting_for_choosing_time)
async def book_or_cancel_time(call: CallbackQuery, state: FSMContext):
    if call.data.split('_')[0] == "booked":
        slot = datetime.strptime(call.data.split('_')[1], "%y-%m-%d %H:%M:%S")
        if slot > datetime.now():
            await state.update_data(slot=slot)
            await MasterTimetable.waiting_for_cancellation.set()
            await call.message.answer("Do you want to cancel booking?", reply_markup=kb_master_cancel_booking)
        else:
            await call.answer(text="The timeslot is already booked", show_alert=True)
    else:
        await call.answer(cache_time=1)
        data = await state.get_data()
        chosen_date = data['chosen_day'].split(' ')[1]
        chosen_time = call.data
        await state.update_data(selected_date=chosen_date, selected_time=int(chosen_time))
        await MasterTimetable.waiting_for_confirmation.set()
        await call.message.answer(f'You are trying to book {call.data}:00 timeslot.\n'
                                  f'Press the <b>"Confirm booking"</b> or <b>"Cancel"</b>',
                                  reply_markup=kb_confirm_booking)


@dp.message_handler(text="Cancel booking", state=MasterTimetable.waiting_for_cancellation)
async def cancel_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    visit = await Timeslot.query.where((Timeslot.datetime == data['slot']) & (Timeslot.master_id == data['master_id'])).gino.first()
    customer = await Customer.query.where(Customer.id == visit.customer_id).gino.first()
    if customer.chat_id:
        await bot.send_message(chat_id=customer.chat_id,
                               text='<b>Notification:</b>\n\n'
                                    'Master has canceled your visit on\n'
                                    f'<b>{data["chosen_day"]}</b> at <b>{visit.datetime.strftime("%H:%M")}</b>')
        await sleep(0.3)
    await visit.delete()
    await message.answer('Visit has been successfully canceled', reply_markup=kb_master_commands)
    await state.finish()


@dp.message_handler(text="Confirm booking", state=MasterTimetable.waiting_for_confirmation)
async def book_confirmation(message: Message, state: FSMContext):
    await message.answer(f'Enter your phone number\n\n'
                         '<em>HINT: valid format 931234567. Don\'t enter +380 </em>',
                         reply_markup=ReplyKeyboardRemove())


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
            try:
                await Timeslot.create(datetime=datetime.combine(chosen_date, chosen_time),
                                      is_free=False,
                                      customer_id=customer.id,
                                      master_id=data['master_id'])
                await message.answer(f"Done!", reply_markup=kb_master_commands)
                await state.finish()
            except UniqueViolationError:
                await message.answer(text=f"<b>Alert:</b>\n\n"
                                          "Customer already has visit at this time!\n"
                                          "Please, chose another timeslot", reply_markup=kb_master_commands)
        else:
            await state.update_data(phone=phone)
            await MasterTimetable.waiting_for_new_customer_name.set()
            await message.answer('Please enter customers name', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(regexp=r'^[^\/].{1,100}$', state=MasterTimetable.waiting_for_new_customer_name)
async def customer_name(message: Message, state: FSMContext):
    data = await state.get_data()
    customer = await Customer.create(name=message.text, phone=data['phone'])
    await Timeslot.create(datetime=datetime.combine(data['chosen_date'], data['chosen_time']),
                          is_free=False,
                          customer_id=customer.id, master_id=data['master_id'])
    await message.answer(f"Done!", reply_markup=kb_master_commands)
    await state.finish()
