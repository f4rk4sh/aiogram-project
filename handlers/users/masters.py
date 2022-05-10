import logging

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp
from keyboards.inline import master_choice, booking_days, time_slots
from keyboards.default import master_info, confirm_booking, masters


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
    await ChosenMaster.next()
    await message.answer(f"You have decided to book {cm['master']}.\n"
                         f"Please choose the day!",
                         reply_markup=booking_days)


@dp.callback_query_handler(lambda c: c.data.__contains__("day") or
                                     c.data.__contains__("Previous week") or
                                     c.data.__contains__("Next week"),
                           state=ChosenMaster.waiting_for_choosing_date)
async def book_day(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)

    # This shit doesn't work yet!
    if call.data.split(':')[1] == "Previous week":
        await call.message.answer(f"You are trying to switch back")
    elif call.data.split(':')[1] == "Next week":
        await call.message.answer(f"You are trying to switch forth")

    else:
        cm = await state.get_data()

        await state.update_data(chosen_day=call.data.split(':')[1])
        await ChosenMaster.next()
        await call.message.answer(f"You are trying to view available slots "
                                  f"on {call.data.split(':')[1]} for {cm['master']}\n"
                                  f"Please, select the available one!",
                                  reply_markup=time_slots)


@dp.callback_query_handler(text_contains="m", state=ChosenMaster.waiting_for_choosing_time)
async def book_time(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)

    cm = await state.get_data()
    logging.info(F"callback {call.data}")
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


