from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, ReplyKeyboardRemove, InputMedia)
from aiogram.utils.callback_data import CallbackData

from filters import date_filters as df
from filters import get_dates, update_dates
from keyboards.default import kb_confirm_booking, kb_master_info, kb_masters
from keyboards.inline import kb_time_slots
from loader import dp
from states import ChosenMaster
from utils.db_api.models import Master, PortfolioPhoto


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
    dates = get_dates(day)
    days_keyboard = get_days_keyboard(day, dates)
    await state.update_data(dates=dates)
    await ChosenMaster.waiting_for_choosing_date.set()
    await message.answer(f"You have decided to book {data['master_name']}.\n"
                         f"Please choose the day!",
                         reply_markup=days_keyboard)


@dp.callback_query_handler(text_contains="day", state=ChosenMaster.waiting_for_choosing_date)
async def book_day(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    await state.update_data(chosen_day=call.data.split(':')[1])
    await ChosenMaster.waiting_for_choosing_time.set()
    await call.message.answer(f"You are trying to view available slots "
                              f"on {call.data.split(':')[1]} for {data['master_name']}\n"
                              f"Please, select the available one!",
                              reply_markup=kb_time_slots)


@dp.callback_query_handler(text_contains="week", state=ChosenMaster.waiting_for_choosing_date)
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


@dp.callback_query_handler(text_contains="m", state=ChosenMaster.waiting_for_choosing_time)
async def book_time(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    data = await state.get_data()
    await ChosenMaster.waiting_for_confirmation.set()
    await call.message.answer(f"You are trying to book {data['master_name']} on {data['chosen_day']} {call.data.split(':')[1]}\n"
                              f"Press the 'Confirm booking' button",
                              reply_markup=kb_confirm_booking)


@dp.message_handler(text="Confirm booking", state=ChosenMaster.waiting_for_confirmation)
async def book_confirmation(message: Message, state: FSMContext):
    await message.answer(f"Please enter your phone number without +380", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=ChosenMaster.waiting_for_confirmation)
async def phone_verification(message: Message, state: FSMContext):
    if len(message.text) != 9 or message.text.startswith(("+", "0")) or not message.text.isnumeric():
        await message.answer(f"Wrong number. Try again")
    else:
        cm = await state.get_data()
        await message.answer(f"Done. {cm['master']}", reply_markup=kb_masters)
        await state.finish()


def get_days_keyboard(day, dates):
    master_callback = CallbackData("booking_days", "day_of_week")
    switching = CallbackData("switch", "switch_to")
    days_kb = [
        [
            InlineKeyboardButton(text=f"{df.week.get(d)} {dates[d-1]}",
                                 callback_data=master_callback.new(day_of_week=f"{df.week.get(d)} {dates[d-1]}"))
        ]
        for d in range(day, len(df.week) + 1)
    ]
    prev_next_bt = [
        InlineKeyboardButton(text="Previous week", callback_data=switching.new(switch_to="Previous week")),
        InlineKeyboardButton(text="Next week", callback_data=switching.new(switch_to="Next week"))
    ]
    days_kb.append(prev_next_bt)
    booking_days = InlineKeyboardMarkup(inline_keyboard=days_kb)
    return booking_days


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


@dp.callback_query_handler(portfolio_photos_callback.filter(), state=ChosenMaster.waiting_for_choosing_booking_or_portfolio)
async def photos_page_handler(call: CallbackQuery, callback_data: dict):
    page = int(callback_data.get('page'))
    master_id = int(callback_data.get('master_id'))
    photos = await PortfolioPhoto.query.where(PortfolioPhoto.master_id == master_id).gino.all()
    photo_data = photos[page]
    photo = InputMedia(type='photo', media=photo_data.photo_id)
    await call.message.edit_media(photo, get_portfolio_photos_keyboard(photos, page))
