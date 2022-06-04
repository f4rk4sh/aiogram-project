from aiogram.dispatcher.filters.state import State, StatesGroup


class SendNotification(StatesGroup):
    recipients = State()
    notification = State()
    confirm = State()
