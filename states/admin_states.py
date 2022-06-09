from aiogram.dispatcher.filters.state import State, StatesGroup


class SendNotification(StatesGroup):
    recipients_selected = State()
    notification_typed = State()
    confirm_selected = State()


class AddMaster(StatesGroup):
    chat_id_typed = State()
    name_typed = State()
    phone_typed = State()
    info_typed = State()


class FireMaster(StatesGroup):
    master_selected = State()
    confirm_selected = State()
