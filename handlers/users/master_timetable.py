from asyncio import sleep
from datetime import date, datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)
from asyncpg import UniqueViolationError
from tortoise.expressions import Q

from data.messages import get_message
from filters import IsMaster
from keyboards.default.kb_customer import kb_confirm_booking
from keyboards.default.kb_master import kb_master_commands, kb_master_cancel_booking
from loader import bot, dp
from states.master_states import MasterTimetable
from utils.db_api.models import Customer, Master, Timeslot
from utils.misc import date_span


@dp.message_handler(IsMaster(), text=["My timetable", "/timetable"], state="*")
async def timetable(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    day = datetime.now().isoweekday()
    keyboard = InlineKeyboardMarkup()
    num_d = 7 - day
    master = await Master.get(chat_id=message.chat.id)
    async for time_inc in date_span(
        start=datetime.now(),
        end=datetime.now() + timedelta(days=num_d),
        delta=timedelta(days=1),
    ):
        if await Timeslot.get_or_none(date=time_inc.date(), master=master):
            keyboard.add(
                InlineKeyboardButton(
                    text=f'❌ {time_inc.strftime("%A %d.%m")} ❌', callback_data="day_off"
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
    last_day = datetime.now() + timedelta(days=num_d)
    await MasterTimetable.day_selected.set()
    await state.update_data(
        last_day=last_day.strftime("%y-%m-%d %H:%M:%S"), master_pk=master.pk
    )
    await message.answer(text=get_message("set_day_master"), reply_markup=keyboard)


@dp.callback_query_handler(
    text_contains="day", state=MasterTimetable.day_selected
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
            if await Timeslot.get_or_none(date=time_inc.date(), master=master):
                time_slot.add(
                    InlineKeyboardButton(
                        text=f'❌ Since {time_inc.strftime("%H:%M")} ❌',
                        callback_data=f'booked_{time_inc.strftime("%y-%m-%d %H:%M:%S")}',
                    )
                )
            else:
                time_slot.add(
                    InlineKeyboardButton(
                        text=f'Since {time_inc.strftime("%H:%M")}',
                        callback_data=time_inc.hour,
                    )
                )
    time_slot.add(InlineKeyboardButton(text=f"🏝 Make day off 🏖", callback_data="make_day_off"))
    time_slot.add(InlineKeyboardButton(text=f"Back to days", callback_data="my_timetable"))
    day_off = date(year=2022, month=int(month), day=int(day)).strftime("%y-%m-%d")
    await state.update_data(chosen_day=call.data, day_off=day_off)
    await MasterTimetable.time_selected.set()
    await call.message.edit_text(text=get_message("day_schedule").format(call.data))
    await call.message.edit_reply_markup(reply_markup=time_slot)


@dp.callback_query_handler(
    text_contains="week", state=MasterTimetable.day_selected
)
async def set_day(call: CallbackQuery, state: FSMContext):
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
        async for time_inc in date_span(
            start=datetime.strptime(data["first_day"], "%y-%m-%d %H:%M:%S")
            - timedelta(days=6),
            end=datetime.strptime(data["first_day"], "%y-%m-%d %H:%M:%S"),
            delta=timedelta(days=1),
        ):
            if await Timeslot.get_or_none(date=time_inc.date(), master=master):
                keyboard.add(
                    InlineKeyboardButton(
                        text=f'❌ {time_inc.strftime("%A %d.%m")} ❌',
                        callback_data="day_off",
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
                        callback_data="day_off",
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
        last_day = datetime.strptime(data["last_day"], "%y-%m-%d %H:%M:%S") + timedelta(
            days=7
        )
        await state.update_data(
            first_day=data["last_day"], last_day=last_day.strftime("%y-%m-%d %H:%M:%S")
        )
        await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(text_contains="my_timetable", state="*")
async def back_to_days(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await timetable(message=call.message, state=state)


@dp.callback_query_handler(
    text_contains="day_off", state=MasterTimetable.day_selected
)
async def day_off(call: CallbackQuery, state: FSMContext):
    await call.answer(text=get_message("alert_day_off_master"), show_alert=True)


@dp.callback_query_handler(
    text_contains="make_day_off", state=MasterTimetable.time_selected
)
async def make_day_off(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    data = await state.get_data()
    master = await Master.get(pk=data["master_pk"])
    await Timeslot.create(
        date=datetime.strptime(data["day_off"], "%y-%m-%d").date(),
        master=master,
    )
    await call.message.answer(
        text=get_message("make_day_off_success"), reply_markup=kb_master_commands
    )


@dp.callback_query_handler(state=MasterTimetable.time_selected)
async def check_booking(call: CallbackQuery, state: FSMContext):
    if call.data.split("_")[0] == "booked":
        slot = datetime.strptime(call.data.split("_")[1], "%y-%m-%d %H:%M:%S")
        if slot > datetime.now():
            await state.update_data(slot=call.data.split("_")[1])
            await MasterTimetable.cancellation_selected.set()
            await call.message.answer(
                text=get_message("cancel_booking_confirm"),
                reply_markup=kb_master_cancel_booking,
            )
        else:
            await call.answer(text=get_message("alert_booked"), show_alert=True)
    else:
        await call.answer(cache_time=1)
        data = await state.get_data()
        chosen_date = data["chosen_day"].split(" ")[1]
        chosen_time = call.data
        await state.update_data(
            selected_date=chosen_date, selected_time=int(chosen_time)
        )
        await MasterTimetable.confirm_selected.set()
        await call.message.answer(
            text=get_message("master_book_timeslot_confirm").format(call.data),
            reply_markup=kb_confirm_booking,
        )


@dp.message_handler(
    text="Cancel booking", state=MasterTimetable.cancellation_selected
)
async def cancel_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    slot = datetime.strptime(data["slot"], "%y-%m-%d %H:%M:%S")
    master = await Master.get(pk=data["master_pk"])
    visit = await Timeslot.filter(Q(datetime=slot) & Q(master=master)).first()
    if visit.customer.chat_id:
        await bot.send_message(
            chat_id=visit.customer.chat_id,
            text=get_message("master_visit_cancel_notify_customer").format(
                data["chosen_day"], visit.datetime.strftime("%H:%M")
            ),
        )
        await sleep(0.3)
    await visit.delete()
    await message.answer(
        text=get_message("master_visit_cancel_success"), reply_markup=kb_master_commands
    )
    await state.finish()


@dp.message_handler(
    text="Confirm booking", state=MasterTimetable.confirm_selected
)
async def set_phone(message: Message, state: FSMContext):
    await message.answer(
        text=get_message("set_phone"),
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message_handler(
    regexp=r"\+380\d{9}", state=MasterTimetable.confirm_selected
)
async def set_name(message: Message, state: FSMContext):
    data = await state.get_data()
    chosen_datetime = datetime(
        year=datetime.now().year,
        month=int(data["selected_date"].split(".")[1]),
        day=int(data["selected_date"].split(".")[0]),
        hour=data["selected_time"],
        minute=0,
        second=0,
    )
    await state.update_data(
        chosen_datetime=chosen_datetime.strftime("%y-%m-%d %H:%M:%S")
    )
    customer = await Customer.get_or_none(phone=message.text)
    master = await Master.get(pk=data["master_pk"])
    if customer:
        try:
            await Timeslot.create(
                datetime=chosen_datetime,
                customer=customer,
                master=master,
            )
            await message.answer(
                text=get_message("book_timeslot_success").format(
                    customer.name, data["selected_date"], data["selected_time"]
                ),
                reply_markup=kb_master_commands,
            )
            await state.finish()
        except UniqueViolationError:
            await message.answer(
                text=get_message("customer_duplication_alert"),
                reply_markup=kb_master_commands,
            )
    else:
        await state.update_data(phone=message.text)
        await MasterTimetable.customer_name_typed.set()
        await message.answer(
            text=get_message("set_customer_name"), reply_markup=ReplyKeyboardRemove()
        )


@dp.message_handler(
    regexp=r"^[^\/].{1,100}$", state=MasterTimetable.customer_name_typed
)
async def create_customer(message: Message, state: FSMContext):
    data = await state.get_data()
    chosen_datetime = datetime.strptime(data["chosen_datetime"], "%y-%m-%d %H:%M:%S")
    customer = await Customer.create(name=message.text, phone=data["phone"])
    master = await Master.get(pk=data["master_pk"])
    await Timeslot.create(
        datetime=chosen_datetime,
        customer=customer,
        master=master,
    )
    await message.answer(
        text=get_message("book_timeslot_success").format(
            customer.name, data["selected_date"], data["selected_time"]
        ),
        reply_markup=kb_master_commands,
    )
    await state.finish()
