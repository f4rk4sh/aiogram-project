import logging

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp
from keyboards.inline import master_choice, time_slots  # , booking_days
from keyboards.default import master_info, confirm_booking, masters
from filters import date_filters as df, get_dates, update_dates
from datetime import datetime, date


class ChosenMaster(StatesGroup):
    waiting_for_choosing_master = State()
    waiting_for_choosing_booking_or_portfolio = State()
    waiting_for_choosing_date = State()
    waiting_for_choosing_time = State()
    waiting_for_confirmation = State()


@dp.message_handler(text="List of our masters")
async def list_of_masters(message: Message):
    await message.answer("Here are our best masters",
                         reply_markup=master_choice)
    await ChosenMaster.waiting_for_choosing_master.set()


@dp.callback_query_handler(text_contains="Master", state=ChosenMaster.waiting_for_choosing_master)
async def chosen_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    await state.update_data(master=call.data.split(':')[1])
    await ChosenMaster.next()
    await call.message.answer(f"You have chosen {call.data.split(':')[1]}.\n"
                              f"Here is his profile.\n"
                              f"Please take a look on the masters best works by pressing the 'Portfolio' button.\n"
                              f"If you want to book this Master, please, press 'Book master' button.",
                              reply_markup=master_info)


@dp.message_handler(text="Book master", state=ChosenMaster.waiting_for_choosing_booking_or_portfolio)
async def book_master(message: Message, state: FSMContext):
    cm = await state.get_data()
    day = datetime.now().isoweekday()
    dates = get_dates(day)
    days_keyboard = get_days_keyboard(day, dates)
    await state.update_data(dates=dates)
    await ChosenMaster.next()
    await message.answer(f"You have decided to book {cm['master']}.\n"
                         f"Please choose the day!",
                         reply_markup=days_keyboard)


@dp.callback_query_handler(text_contains="day", state=ChosenMaster.waiting_for_choosing_date)
async def book_day(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    cm = await state.get_data()
    await state.update_data(chosen_day=call.data.split(':')[1])
    await ChosenMaster.next()
    await call.message.answer(f"You are trying to view available slots "
                              f"on {call.data.split(':')[1]} for {cm['master']}\n"
                              f"Please, select the available one!",
                              reply_markup=time_slots)


@dp.callback_query_handler(text_contains="week", state=ChosenMaster.waiting_for_choosing_date)
async def book_day(call: CallbackQuery, state: FSMContext):
    cm = await state.get_data()
    dates = cm['dates']
    today = str(datetime.now().strftime("%d.%m"))
    first_day_in_dates = int(dates[0].split('.')[0])
    if int(today.split('.')[0]) > first_day_in_dates and call.data.split(':')[1] == "Previous week":
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
    cm = await state.get_data()
    await ChosenMaster.next()
    await call.message.answer(f"You are trying to book {cm['master']} on {cm['chosen_day']} {call.data.split(':')[1]}\n"
                              f"Press the 'Confirm booking' button",
                              reply_markup=confirm_booking)


@dp.message_handler(text="Confirm booking", state=ChosenMaster.waiting_for_confirmation)
async def book_confirmation(message: Message, state: FSMContext):
    await message.answer(f"Please enter your phone number without +380", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=ChosenMaster.waiting_for_confirmation)
async def phone_verification(message: Message, state: FSMContext):
    if len(message.text) != 9 or message.text.startswith(("+", "0")) or not message.text.isnumeric():
        await message.answer(f"Wrong number. Try again")
    else:
        cm = await state.get_data()
        await message.answer(f"Done. {cm['master']}", reply_markup=masters)
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

