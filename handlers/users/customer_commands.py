import logging
import os
from asyncio import sleep
from datetime import date, datetime, time, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMedia,
    Message,
)
from aiogram.utils.exceptions import ChatNotFound
from asyncpg import UniqueViolationError

from data.messages import get_message
from keyboards.default.kb_customer import kb_customer_commands, kb_master_info, kb_confirm_booking, kb_request_contact
from keyboards.inline.kb_inline_customer import get_portfolio_photos_keyboard, portfolio_photos_callback
from loader import bot, dp
from states.customer_states import BookMaster
from utils.db_api.models import Customer, Master, PortfolioPhoto, Timeslot
from utils.misc import date_span


@dp.message_handler(text=["Our masters", "/masters"], state="*")
async def set_master(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    masters = await Master.filter(is_active=True)
    if masters:
        kb_master_list = InlineKeyboardMarkup()
        for master in masters:
            kb_master_list.add(
                InlineKeyboardButton(text=master.name, callback_data=master.pk)
            )
        await BookMaster.master_selected.set()
        await message.answer(
            text=get_message("master_list"),
            reply_markup=kb_master_list,
        )
    else:
        await message.answer(
            text=get_message("alert_no_master"), reply_markup=kb_customer_commands
        )


@dp.callback_query_handler(state=BookMaster.master_selected)
async def master_info(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    master = await Master.get(pk=int(call.data))
    await state.update_data(
        master_pk=int(call.data), master_name=master.name, master_info=master.info
    )
    await BookMaster.book_or_portfolio_selected.set()
    if master.photo_id:
        await call.message.answer_photo(
            photo=master.photo_id,
            caption=get_message("master_info").format(master.name, master.info),
            reply_markup=kb_master_info,
        )
    else:
        await call.message.answer(
            text=get_message("master_info").format(master.name, master.info),
            reply_markup=kb_master_info,
        )


@dp.message_handler(
    text=["Book master"],
    state=BookMaster.book_or_portfolio_selected,
)
async def set_day(message: Message, state: FSMContext):
    gotten_state = await state.get_state()
    if gotten_state.split(":")[1] != "book_or_portfolio_selected":
        data = await state.get_data()
        list_keys = []
        for key in data:
            if key not in ["master_pk", "master_name", "master_info"]:
                list_keys.append(key)
        for key in list_keys:
            del data[key]
    else:
        data = await state.get_data()
    day = datetime.now().isoweekday()
    keyboard = InlineKeyboardMarkup()
    num_d = 7 - day
    master = await Master.get(pk=data["master_pk"])
    async for time_inc in date_span(
        start=datetime.now(),
        end=datetime.now() + timedelta(days=num_d),
        delta=timedelta(days=1),
    ):
        if await Timeslot.get_or_none(date=time_inc.date(), master=master):
            keyboard.add(
                InlineKeyboardButton(
                    text=f'❌ {time_inc.strftime("%A %d.%m")} ❌', callback_data="rest"
                )
            )
        else:
            keyboard.add(
                InlineKeyboardButton(
                    text=f'{time_inc.strftime("%A %d.%m")}',
                    callback_data=f'{time_inc.strftime("%A %d.%m")}',
                )
            )
    keyboard.add(
        InlineKeyboardButton(text="Previous week", callback_data="Previous week"),
        InlineKeyboardButton(text="Next week", callback_data="Next week"),
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Back to masters", callback_data="back"
        )
    )
    last_day = datetime.now() + timedelta(days=num_d)
    await state.update_data(last_day=last_day.strftime("%y-%m-%d %H:%M:%S"))
    await BookMaster.day_selected.set()
    await message.answer(
        text=get_message("set_day").format(data["master_name"]),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(
    text_contains="day", state=BookMaster.day_selected
)
async def set_time(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    data = await state.get_data()
    chosen_date = call.data.split(" ")
    month = chosen_date[1].split(".")[1]
    day = chosen_date[1].split(".")[0]
    time_slot = InlineKeyboardMarkup()
    master = await Master.get(pk=data["master_pk"])
    async for time_inc in date_span(
        start=datetime(2022, int(month), int(day), 10),
        end=datetime(2022, int(month), int(day), 19),
        delta=timedelta(hours=1),
    ):
        if time_inc > datetime.now():
            if await Timeslot.get_or_none(datetime=time_inc, master=master):
                time_slot.add(
                    InlineKeyboardButton(
                        text=f'❌ Since {time_inc.strftime("%H:%M")} ❌',
                        callback_data="booked",
                    )
                )
            else:
                time_slot.add(
                    InlineKeyboardButton(
                        text=f'Since {time_inc.strftime("%H:%M")}',
                        callback_data=time_inc.hour,
                    )
                )
    time_slot.add(
        InlineKeyboardButton(
            text="Back to days", callback_data="back"
        )
    )
    await state.update_data(chosen_day=call.data)
    await BookMaster.time_selected.set()
    await call.message.edit_text(text=get_message("set_time").format(call.data, data["master_name"]))
    await call.message.edit_reply_markup(reply_markup=time_slot)


@dp.callback_query_handler(
    text_contains="week", state=BookMaster.day_selected
)
async def set_day_week(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    master = await Master.get(pk=data["master_pk"])
    try:
        future = datetime.now() > datetime.strptime(data["first_day"], "%y-%m-%d %H:%M:%S")
    except KeyError:
        future = True
    if call.data == "Previous week" and future:
        await call.answer(text=get_message("alert_past"), show_alert=True)
    elif call.data == "Previous week":
        keyboard = InlineKeyboardMarkup()
        if abs(datetime.strptime(data["first_day"], "%y-%m-%d %H:%M:%S") - datetime.now()) < timedelta(days=7):
            day = datetime.now().isoweekday()
            num_d = 7 - day
            start = datetime.now()
            end = datetime.now() + timedelta(days=num_d)
        else:
            start = datetime.strptime(data["first_day"], "%y-%m-%d %H:%M:%S") - timedelta(days=6)
            end = datetime.strptime(data["first_day"], "%y-%m-%d %H:%M:%S")
        async for time_inc in date_span(
            start=start,
            end=end,
            delta=timedelta(days=1),
        ):
            if time_inc > datetime.now() - timedelta(days=1):
                if await Timeslot.get_or_none(date=time_inc.date(), master=master):
                    keyboard.add(
                        InlineKeyboardButton(
                            text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                            callback_data="rest",
                        )
                    )
                else:
                    keyboard.add(
                        InlineKeyboardButton(
                            text=f'{time_inc.strftime("%A %d.%m")}',
                            callback_data=f'{time_inc.strftime("%A %d.%m")}',
                        )
                    )

        keyboard.add(
            InlineKeyboardButton(text="Previous week", callback_data="Previous week"),
            InlineKeyboardButton(text="Next week", callback_data="Next week"),
        )
        keyboard.add(
            InlineKeyboardButton(
                text=f"Back to masters",
                callback_data="back",
            )
        )
        first_day = datetime.strptime(
            data["first_day"], "%y-%m-%d %H:%M:%S"
        ) - timedelta(days=7)
        await state.update_data(
            first_day=first_day.strftime("%y-%m-%d %H:%M:%S"),
            last_day=data["first_day"],
        )
        await call.message.edit_reply_markup(reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup()
        async for time_inc in date_span(
            start=datetime.strptime(data["last_day"], "%y-%m-%d %H:%M:%S")
            + timedelta(days=1),
            end=datetime.strptime(data["last_day"], "%y-%m-%d %H:%M:%S")
            + timedelta(days=7),
            delta=timedelta(days=1),
        ):
            if await Timeslot.get_or_none(date=time_inc.date(), master=master):
                keyboard.add(
                    InlineKeyboardButton(
                        text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                        callback_data="rest",
                    )
                )
            else:
                keyboard.add(
                    InlineKeyboardButton(
                        text=f'{time_inc.strftime("%A %d.%m")}',
                        callback_data=f'{time_inc.strftime("%A %d.%m")}',
                    )
                )
        keyboard.add(
            InlineKeyboardButton(text="Previous week", callback_data="Previous week"),
            InlineKeyboardButton(text="Next week", callback_data="Next week"),
        )
        keyboard.add(
            InlineKeyboardButton(
                text=f"Back to masters",
                callback_data="back",
            )
        )
        last_day = datetime.strptime(data["last_day"], "%y-%m-%d %H:%M:%S") + timedelta(
            days=7
        )
        await state.update_data(
            first_day=data["last_day"], last_day=last_day.strftime("%y-%m-%d %H:%M:%S")
        )
        await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(text_contains="back", state="*")
async def back(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    gotten_state = await state.get_state()
    if gotten_state.split(":")[1] == "day_selected":
        await set_master(call.message)
    else:
        await set_day(call.message, state)


@dp.callback_query_handler(
    text_contains="rest", state=BookMaster.day_selected
)
async def day_off(call: CallbackQuery, state: FSMContext):
    await call.answer(text=get_message("alert_day_off"), show_alert=True)


@dp.callback_query_handler(state=BookMaster.time_selected)
async def check_booking(call: CallbackQuery, state: FSMContext):
    if call.data == "booked":
        await call.answer(text=get_message("alert_booked"), show_alert=True)
    else:
        await call.answer(cache_time=1)
        data = await state.get_data()
        chosen_date = data["chosen_day"].split(" ")[1]
        chosen_time = call.data
        await state.update_data(
            selected_date=chosen_date, selected_time=int(chosen_time)
        )
        await BookMaster.confirm_selected.set()
        await call.message.answer(
            text=get_message("confirm_booking").format(
                data["master_name"], data["chosen_day"], call.data
            ),
            reply_markup=kb_confirm_booking,
        )


@dp.message_handler(text="Confirm booking", state=BookMaster.confirm_selected)
async def confirm_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = message.chat.id
    customer = await Customer.get_or_none(chat_id=chat_id)
    if customer:
        chosen_date = date(
            year=datetime.now().year,
            month=int(data["selected_date"].split(".")[1]),
            day=int(data["selected_date"].split(".")[0]),
        )
        chosen_time = time(hour=data["selected_time"], minute=0, second=0)
        try:
            master = await Master.get(pk=data["master_pk"])
            await Timeslot.create(
                datetime=datetime.combine(chosen_date, chosen_time),
                customer=customer,
                master=master,
            )
            await message.answer(
                text=get_message("book_success").format(
                    master.name, data["chosen_day"], data["selected_time"]
                ),
                reply_markup=kb_customer_commands,
            )
            try:
                await bot.send_message(
                    chat_id=master.chat_id,
                    text=get_message("book_notify_master").format(
                        data["chosen_day"],
                        data["selected_time"],
                        customer.name,
                        customer.phone,
                    ),
                )
                await sleep(0.3)
            except ChatNotFound:
                logging.info(f"ChatNotFound: chat id - {master.chat_id}")
                await message.answer(text=get_message("alert_no_master_chat_id").format(str(os.getenv("PHONE_NUM"))))
            await state.finish()
        except UniqueViolationError:
            await message.answer(
                text=get_message("alert_duplication"),
                reply_markup=kb_customer_commands,
            )
    else:
        await message.answer(
            text=get_message("send_contact"),
            reply_markup=kb_request_contact,
        )


@dp.message_handler(
    content_types=["contact"], state=BookMaster.confirm_selected
)
async def create_customer(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = message.chat.id
    name = message.from_user.full_name
    phone = (
        f"+{message.contact.phone_number}"
        if len(message.contact.phone_number) == 12
        else f"{message.contact.phone_number}"
    )
    customer = await Customer.get_or_none(phone=phone)
    if not customer:
        await Customer.create(chat_id=chat_id, name=name, phone=phone)
    else:
        if customer.chat_id is None:
            customer.chat_id = message.from_user.id
            await customer.save()
    chosen_date = date(
        year=datetime.now().year,
        month=int(data["selected_date"].split(".")[1]),
        day=int(data["selected_date"].split(".")[0]),
    )
    chosen_time = time(hour=data["selected_time"], minute=0, second=0)
    customer = await Customer.filter(chat_id=chat_id).first()
    master = await Master.get(pk=data["master_pk"])
    await Timeslot.create(
        datetime=datetime.combine(chosen_date, chosen_time),
        customer=customer,
        master=master,
    )
    await message.answer(
        text=get_message("book_success").format(
            master.name, chosen_date, data["selected_time"]
        ),
        reply_markup=kb_customer_commands,
    )
    try:
        await bot.send_message(
            chat_id=master.chat_id,
            text=get_message("book_notify_master").format(
                data["chosen_day"], data["selected_time"], customer.name, customer.phone
            ),
        )
        await sleep(0.3)
    except ChatNotFound:
        logging.info(f"ChatNotFound: chat id - {master.chat_id}")
        await message.answer(text=get_message("alert_no_master_chat_id").format(str(os.getenv("PHONE_NUM"))))
    await state.finish()


@dp.message_handler(
    text="Portfolio", state=BookMaster.book_or_portfolio_selected
)
async def portfolio(message: Message, state: FSMContext):
    data = await state.get_data()
    master = await Master.get(pk=data["master_pk"])
    photos = await PortfolioPhoto.filter(master=master)
    if photos:
        photo_data = photos[0]
        await message.answer_photo(
            photo=photo_data.photo_id,
            reply_markup=get_portfolio_photos_keyboard(photos, master),
        )
    else:
        await message.answer(
            text=get_message("alert_no_photos").format(data["master_name"]),
            reply_markup=kb_customer_commands,
        )


@dp.callback_query_handler(
    portfolio_photos_callback.filter(),
    state=BookMaster.book_or_portfolio_selected,
)
async def photos_page_handler(call: CallbackQuery, callback_data: dict):
    page = int(callback_data["page"])
    master = await Master.get(pk=callback_data["master_pk"])
    photos = await PortfolioPhoto.filter(master=master)
    photo_data = photos[page]
    photo = InputMedia(type="photo", media=photo_data.photo_id)
    await call.message.edit_media(
        photo, get_portfolio_photos_keyboard(photos, master, page)
    )
