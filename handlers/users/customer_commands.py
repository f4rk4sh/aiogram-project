import asyncio
import logging
from datetime import date, time, datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, ReplyKeyboardRemove, InputMedia)
from aiogram.utils.callback_data import CallbackData

from keyboards.default import kb_confirm_booking, kb_master_info, kb_masters, kb_request_contact
from loader import dp
from states import ChosenMaster
from utils.db_api.models import Master, Customer, Timeslot, PortfolioPhoto


@dp.message_handler(text=["List of our masters", "/masters"])
async def list_of_masters(message: Message):
    masters = await Master.query.gino.all()
    kb_master_list = InlineKeyboardMarkup()
    for master in masters:
        kb_master_list.add(InlineKeyboardButton(text=master.name, callback_data=master.id))
    await ChosenMaster.waiting_for_choosing_master.set()
    await message.answer("Here are our best masters", reply_markup=kb_master_list)


@dp.callback_query_handler(state=ChosenMaster.waiting_for_choosing_master)
async def chosen_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    master = await Master.query.where(Master.id == int(call.data)).gino.first()
    await state.update_data(master_id=int(call.data), master_name=master.name, master_info=master.info)
    await ChosenMaster.waiting_for_choosing_booking_or_portfolio.set()
    text = f"<b>Name:</b> {master.name}\n" \
           f"<b>Info:</b> {master.info}\n\n" \
           "Please take a look on the masters best works by pressing the <b>\"Portfolio\"</b> button.\n\n" \
           "If you want to book this Master, please, press <b>\"Book master\"</b> button."
    if master.photo_id:
        await call.message.answer_photo(master.photo_id, caption=text, reply_markup=kb_master_info)
    else:
        await call.message.answer(text=text, reply_markup=kb_master_info)


@dp.message_handler(text=["Book master", '/book_master'], state=ChosenMaster.waiting_for_choosing_booking_or_portfolio)
async def book_master(message: Message, state: FSMContext):
    data = await state.get_data()
    day = datetime.now().isoweekday()
    keyboard = InlineKeyboardMarkup()
    num_d = 7 - day
    async for time_inc in date_span(start=datetime.now(),
                                    end=datetime.now() + timedelta(days=num_d),
                                    delta=timedelta(days=1)):
        keyboard.add(InlineKeyboardButton(text=f'{time_inc.strftime("%A %d.%m")}',
                                          callback_data=f'{time_inc.strftime("%A %d.%m")}'))
    keyboard.add(InlineKeyboardButton(text="Previous week", callback_data='Previous week'),
                 InlineKeyboardButton(text="Next week", callback_data='Next week'))
    await state.update_data(dima_last_day=datetime.now() + timedelta(days=num_d))
    await ChosenMaster.waiting_for_choosing_date.set()
    await message.answer(f"You have decided to book {data['master_name']}.\n"
                         f"Please choose the day!",
                         reply_markup=keyboard)


@dp.callback_query_handler(text_contains="day", state=ChosenMaster.waiting_for_choosing_date)
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
        if await Timeslot.query.where(((Timeslot.date == time_inc.date()) & (Timeslot.time == time_inc.time()) & (
                Timeslot.master_id == data['master_id']))).gino.one_or_none():
            time_slot.add(InlineKeyboardButton(text=f'❌ Since {time_inc.strftime("%H:%M")} ❌', callback_data="booked"))
        else:
            time_slot.add(InlineKeyboardButton(text=f'Since {time_inc.strftime("%H:%M")}', callback_data=time_inc.hour))

    await state.update_data(chosen_day=call.data)
    await ChosenMaster.waiting_for_choosing_time.set()
    await call.message.answer(f"You are trying to view available slots "
                              f"on {call.data} for {data['master_name']}\n"
                              f"Please, select the available one!",
                              reply_markup=time_slot)


@dp.callback_query_handler(text_contains="week", state=ChosenMaster.waiting_for_choosing_date)
async def book_day(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if call.data == "Previous week" and datetime.now() > data['dima_first_day']:
        await call.answer(text="You can't navigate to the past", show_alert=True)
    elif call.data == "Previous week":
        keyboard = InlineKeyboardMarkup()
        async for time_inc in date_span(start=data['dima_first_day'] - timedelta(days=6),
                                        end=data['dima_first_day'],
                                        delta=timedelta(days=1)):
            if time_inc > datetime.now() - timedelta(days=1):
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
            keyboard.add(InlineKeyboardButton(text=f'{time_inc.strftime("%A %d.%m")}',
                                              callback_data=f'{time_inc.strftime("%A %d.%m")}'))
        keyboard.add(InlineKeyboardButton(text="Previous week", callback_data='Previous week'),
                     InlineKeyboardButton(text="Next week", callback_data='Next week'))
        await state.update_data(dima_first_day=data['dima_last_day'],
                                dima_last_day=data['dima_last_day'] + timedelta(days=7))
        await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(state=ChosenMaster.waiting_for_choosing_time)
async def book_time(call: CallbackQuery, state: FSMContext):
    if call.data == "booked":
        await call.answer(text="The timeslot is already booked", show_alert=True)
    else:
        await call.answer(cache_time=1)
        data = await state.get_data()
        chosen_date = data['chosen_day'].split(' ')[1]
        chosen_time = call.data
        await state.update_data(selected_date=chosen_date, selected_time=int(chosen_time))
        await ChosenMaster.waiting_for_confirmation.set()
        await call.message.answer(
            f"You are trying to book {data['master_name']} on {data['chosen_day']} at {call.data}\n"
            f"Press the 'Confirm booking' button",
            reply_markup=kb_confirm_booking)


@dp.message_handler(text="Confirm booking", state=ChosenMaster.waiting_for_confirmation)
async def book_confirmation(message: Message, state: FSMContext):
    await message.answer(f"Please send us your phone number", reply_markup=kb_request_contact)


@dp.message_handler(content_types=['contact'], state=ChosenMaster.waiting_for_confirmation)
async def phone_verification(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = message.chat.id
    name = message.from_user.full_name
    phone = f'+{message.contact.phone_number}'
    customer = await Customer.query.where(Customer.phone == phone).gino.one_or_none()
    if not customer:
        await Customer.create(chat_id=chat_id, name=name, phone=phone)
    else:
        if customer.chat_id is None:
            await customer.update(chat_id=message.from_user.id)
    chosen_date = date(year=datetime.now().year,
                       month=int(data['selected_date'].split('.')[1]),
                       day=int(data['selected_date'].split('.')[0]))
    chosen_time = time(hour=data['selected_time'],
                       minute=0,
                       second=0)
    customer_id = await Customer.select('id').where(Customer.chat_id == chat_id).gino.scalar()
    master_id = data['master_id']
    await Timeslot.create(date=chosen_date,
                          time=chosen_time,
                          is_free=False,
                          customer_id=customer_id, master_id=master_id)
    await message.answer(f"Done!", reply_markup=kb_masters)
    await state.finish()


async def date_span(start, end, delta):
    current_date = start
    while current_date <= end:
        yield current_date
        current_date += delta


portfolio_photos_callback = CallbackData('Photo', 'page', 'master_id')


def get_portfolio_photos_keyboard(photos, page: int = 0):
    keyboard = InlineKeyboardMarkup(row_width=3)
    has_next_page = len(photos) > page + 1
    if page != 0:
        keyboard.add(
            InlineKeyboardButton(
                text='Previous photo',
                callback_data=portfolio_photos_callback.new(page=page - 1, master_id=photos[0].master_id)
            )
        )
    if has_next_page:
        keyboard.add(
            InlineKeyboardButton(
                text='Next photo',
                callback_data=portfolio_photos_callback.new(page=page + 1, master_id=photos[0].master_id)
            )
        )
    return keyboard


@dp.message_handler(text='Portfolio', state=ChosenMaster.waiting_for_choosing_booking_or_portfolio)
async def portfolio(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = await PortfolioPhoto.query.where(PortfolioPhoto.master_id == data['master_id']).gino.all()
    if photos:
        photo_data = photos[0]
        await message.answer_photo(photo=photo_data.photo_id, reply_markup=get_portfolio_photos_keyboard(photos))
    else:
        await message.answer(f'{data["master_name"]} has no portfolio photos yet', reply_markup=kb_masters)


@dp.callback_query_handler(portfolio_photos_callback.filter(),
                           state=ChosenMaster.waiting_for_choosing_booking_or_portfolio)
async def photos_page_handler(call: CallbackQuery, callback_data: dict):
    page = int(callback_data.get('page'))
    master_id = int(callback_data.get('master_id'))
    photos = await PortfolioPhoto.query.where(PortfolioPhoto.master_id == master_id).gino.all()
    photo_data = photos[page]
    photo = InputMedia(type='photo', media=photo_data.photo_id)
    await call.message.edit_media(photo, get_portfolio_photos_keyboard(photos, page))
