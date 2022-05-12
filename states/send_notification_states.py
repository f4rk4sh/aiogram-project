from aiogram.dispatcher.filters.state import StatesGroup, State


class SendNotification(StatesGroup):
    recipients = State()
    notification = State()
    confirm = State()
