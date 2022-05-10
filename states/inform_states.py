from aiogram.dispatcher.filters.state import StatesGroup, State


class Inform(StatesGroup):
    recipients = State()
    notification = State()
    confirm = State()
