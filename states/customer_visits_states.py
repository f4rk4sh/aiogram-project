from aiogram.dispatcher.filters.state import StatesGroup, State


class CustomerVisits(StatesGroup):
    visits = State()


class CancelVisit(StatesGroup):
    visit = State()
