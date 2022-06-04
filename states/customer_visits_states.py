from aiogram.dispatcher.filters.state import State, StatesGroup


class CustomerVisits(StatesGroup):
    visits = State()


class CancelVisit(StatesGroup):
    visit = State()
