from aiogram.dispatcher.filters.state import State, StatesGroup


class ChosenMaster(StatesGroup):
    waiting_for_choosing_master = State()
    waiting_for_choosing_booking_or_portfolio = State()
    waiting_for_choosing_date = State()
    waiting_for_choosing_time = State()
    waiting_for_confirmation = State()
