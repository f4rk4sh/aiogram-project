# import asyncio
import logging
from asyncio import sleep
from datetime import date, time, datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, ReplyKeyboardRemove, InputMedia)
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import ChatNotFound
from asyncpg import UniqueViolationError

from keyboards.default import kb_confirm_booking, kb_master_info, kb_masters, kb_request_contact
from loader import bot, dp
from states import ChosenMaster
from utils.db_api.models import Master, Customer, Timeslot, PortfolioPhoto
from utils.misc import date_span


@dp.message_handler(text=["List of our masters", "/masters"], state="*")
async def list_of_masters(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    masters = await Master.query.gino.all()
    kb_master_list = InlineKeyboardMarkup()
    for master in masters:
        kb_master_list.add(InlineKeyboardButton(text=master.name, callback_data=master.id))
    await ChosenMaster.waiting_for_choosing_master.set()
    await message.answer("<b>Here are our best masters!</b>\n"
                         "Please chose one",
                         reply_markup=kb_master_list)


@dp.callback_query_handler(state=ChosenMaster.waiting_for_choosing_master)
async def chosen_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
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
    # Это ДИЧАЙШИЙ костыль!!! Он позволяет вернуться из выбора времени к выбору дня.
    # Этот костыль необходимо убрать, но для  этого нужно как-то вызвать этот хендлер в функции back_to_masters :(
    # Если бы мы знали как это сделать - мы бы это сделали, но мы не знаем как это сделать©️
    gotten_sate = await state.get_state()
    if gotten_sate.split(':')[1] != "waiting_for_choosing_booking_or_portfolio":
        data = await state.get_data()
        list_keys = []
        for key in data:
            if key not in ['master_id', 'master_name', 'master_info']:
                list_keys.append(key)
        for key in list_keys:
            del data[key]
    else:
        data = await state.get_data()
    # Конец ДИЧАЙШЕГО костыля

    day = datetime.now().isoweekday()
    keyboard = InlineKeyboardMarkup()
    num_d = 7 - day
    async for time_inc in date_span(start=datetime.now(),
                                    end=datetime.now() + timedelta(days=num_d),
                                    delta=timedelta(days=1)):
        if await Timeslot.query.where((Timeslot.date == time_inc.date()) & (Timeslot.master_id == data['master_id'])).gino.one_or_none():
            keyboard.add(InlineKeyboardButton(text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                                              callback_data=f'busy'))
        else:
            keyboard.add(InlineKeyboardButton(text=f'{time_inc.strftime("%A %d.%m")}',
                                              callback_data=f'{time_inc.strftime("%A %d.%m")}'))
    keyboard.add(InlineKeyboardButton(text="Previous week", callback_data='Previous week'),
                 InlineKeyboardButton(text="Next week", callback_data='Next week'))
    keyboard.add(InlineKeyboardButton(text=f'Back to choosing masters',
                                      callback_data="Back to choosing masters"))
    await state.update_data(dima_last_day=datetime.now() + timedelta(days=num_d))
    await ChosenMaster.waiting_for_choosing_date.set()
    await message.answer(f"You have decided to book <b>{data['master_name'].capitalize()}</b>\n"
                         f"Please choose the day!",
                         reply_markup=keyboard)


@dp.callback_query_handler(text_contains="day", state=ChosenMaster.waiting_for_choosing_date)
async def book_day(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    data = await state.get_data()
    chosen_date = call.data.split(' ')
    month = chosen_date[1].split('.')[1]
    day = chosen_date[1].split('.')[0]
    time_slot = InlineKeyboardMarkup()
    async for time_inc in date_span(start=datetime(2022, int(month), int(day), 10),
                                    end=datetime(2022, int(month), int(day), 19),
                                    delta=timedelta(hours=1)):
        if time_inc > datetime.now():
            if await Timeslot.query.where(((Timeslot.datetime == time_inc) &
                                           (Timeslot.master_id == data['master_id']))).gino.one_or_none():
                time_slot.add(InlineKeyboardButton(text=f'❌ Since {time_inc.strftime("%H:%M")} ❌',
                                                   callback_data="booked"))
            else:
                time_slot.add(InlineKeyboardButton(text=f'Since {time_inc.strftime("%H:%M")}',
                                                   callback_data=time_inc.hour))
    time_slot.add(InlineKeyboardButton(text=f'Back to choosing days',
                                       callback_data="Back to choosing days"))
    await state.update_data(chosen_day=call.data)
    await ChosenMaster.waiting_for_choosing_time.set()
    await call.message.answer(f"<b>Note:</b>\n\n"
                              f"You are trying to view available slots on\n"
                              f"<b>{call.data}</b> for <b>{data['master_name'].capitalize()}</b>\n"
                              f"Please, select the available one!",
                              reply_markup=time_slot)


@dp.callback_query_handler(text_contains="Back", state="*")
async def back_to_masters(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    gotten_sate = await state.get_state()
    if gotten_sate.split(':')[1] == "waiting_for_choosing_date":
        await list_of_masters(call.message)
    else:
        await book_master(message=call.message, state=state)


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
                if await Timeslot.query.where(
                        (Timeslot.date == time_inc.date()) & (
                                Timeslot.master_id == data['master_id'])).gino.one_or_none():
                    keyboard.add(InlineKeyboardButton(text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                                                      callback_data=f'busy'))
                else:
                    keyboard.add(InlineKeyboardButton(text=f'{time_inc.strftime("%A %d.%m")}',
                                                      callback_data=f'{time_inc.strftime("%A %d.%m")}'))

        keyboard.add(InlineKeyboardButton(text="Previous week", callback_data='Previous week'),
                     InlineKeyboardButton(text="Next week", callback_data='Next week'))
        keyboard.add(InlineKeyboardButton(text=f'Back to choosing masters',
                                          callback_data="Back to choosing masters"))
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
        keyboard.add(InlineKeyboardButton(text=f'Back to choosing masters',
                                          callback_data="Back to choosing masters"))
        await state.update_data(dima_first_day=data['dima_last_day'],
                                dima_last_day=data['dima_last_day'] + timedelta(days=7))
        await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(text_contains="busy", state=ChosenMaster.waiting_for_choosing_date)
async def make_day_off(call: CallbackQuery, state: FSMContext):
    await call.answer(text="This is the masters day off.", show_alert=True)


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
            f"<b>Alert:</b>\n\n"
            f"You are trying to book <b>{data['master_name'].capitalize()}</b> on "
            f"<b>{data['chosen_day']}</b> at <b>{call.data}:00</b>\n"
            f"Press the <b>'Confirm booking'</b> to proceed\n"
            f"or <b>'Cancel'</b> if you want to abort booking.",
            reply_markup=kb_confirm_booking)


@dp.message_handler(text="Confirm booking", state=ChosenMaster.waiting_for_confirmation)
async def book_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = message.chat.id
    customer = await Customer.query.where(Customer.chat_id == chat_id).gino.one_or_none()
    if customer:
        chosen_date = date(year=datetime.now().year,
                           month=int(data['selected_date'].split('.')[1]),
                           day=int(data['selected_date'].split('.')[0]))
        chosen_time = time(hour=data['selected_time'],
                           minute=0,
                           second=0)
        try:
            await Timeslot.create(datetime=datetime.combine(chosen_date, chosen_time),
                                  is_free=False,
                                  customer_id=customer.id, master_id=data['master_id'])
            master = await Master.query.where(Master.id == data["master_id"]).gino.first()
            await message.answer(f'<b>You have successfully booked {master.name}!</b>\n'
                                 f'Pleased to see you on {data["chosen_day"]} at {data["selected_time"]}:00.',
                                 reply_markup=kb_masters)
            master = await Master.query.where(Master.id == data['master_id']).gino.first()
            try:
                await bot.send_message(chat_id=master.chat_id,
                                       text='<b>Notification:</b>\n\n'
                                            f'You have gotten a new booking\n\n'
                                            f'<b>Date:</b> {data["chosen_day"]}\n'
                                            f'<b>Time:</b> {data["selected_time"]}:00\n'
                                            f'<b>Customer:</b> {customer.name.capitalize()}, {customer.phone}')
                await sleep(0.3)
            except ChatNotFound:
                logging.info(f'ChatNotFound: chat id - {master.chat_id}')
                await message.answer(
                    f'<b>Alert:</b>\n\n'
                    f'Notification has not been sent! Masters telegram account is unavailable. Please call us.'
                )
            await state.finish()
        except UniqueViolationError:
            await message.answer(text=f"<b>Alert:</b>\n\n"
                                      "You already have visit at this time! Go to your visits for more details.\n"
                                      "Please, chose another timeslot", reply_markup=kb_masters)
    else:
        await message.answer(f'Please send us your phone number by pressing <b>"Send contact"</b> button',
                             reply_markup=kb_request_contact)


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
    await Timeslot.create(datetime=datetime.combine(chosen_date, chosen_time),
                          is_free=False,
                          customer_id=customer_id, master_id=master_id)
    await message.answer(f"Done!", reply_markup=kb_masters)
    master = await Master.query.where(Master.id == data['master_id']).gino.first()
    customer = await Customer.query.where(Customer.chat_id == chat_id).gino.first()
    try:
        await bot.send_message(chat_id=master.chat_id,
                               text='<b>Notification:</b>\n\n'
                                    f'You have gotten a new booking\n\n'
                                    f'<b>Date:</b> {data["chosen_day"]}\n'
                                    f'<b>Time:</b> {data["selected_time"]}:00\n'
                                    f'<b>Customer:</b> {customer.name.capitalize()}, {phone}')
        await sleep(0.3)
    except ChatNotFound:
        logging.info(f'ChatNotFound: chat id - {master.chat_id}')
        await message.answer(
            f'<b>Alert:</b>\n\n'
            f'Notification has not been sent! Masters telegram account is unavailable. Please call us.'
        )
    await state.finish()


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
