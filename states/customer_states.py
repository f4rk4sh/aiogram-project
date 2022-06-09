from aiogram.dispatcher.filters.state import State, StatesGroup


class BookMaster(StatesGroup):
    master_selected = State()
    book_or_portfolio_selected = State()
    day_selected = State()
    time_selected = State()
    confirm_selected = State()


class CustomerVisits(StatesGroup):
    visits = State()


class CancelVisit(StatesGroup):
    visit_selected = State()
