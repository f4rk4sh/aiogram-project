from aiogram.dispatcher.filters.state import StatesGroup, State


class MasterTimetable(StatesGroup):
    waiting_for_choosing_day = State()
    waiting_for_choosing_time = State()
    waiting_for_cancellation = State()
    waiting_for_booking = State()
    waiting_for_confirmation = State()
    waiting_for_new_customer_name = State()
