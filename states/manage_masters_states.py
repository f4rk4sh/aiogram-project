from aiogram.dispatcher.filters.state import State, StatesGroup


class AddMaster(StatesGroup):
    chat_id = State()
    name = State()
    phone = State()
    info = State()


class FireMaster(StatesGroup):
    select = State()
    confirm = State()
