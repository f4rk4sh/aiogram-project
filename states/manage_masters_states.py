from aiogram.dispatcher.filters.state import StatesGroup, State


class AddMaster(StatesGroup):
    chat_id = State()
    name = State()
    phone = State()
    info = State()


class DeleteMaster(StatesGroup):
    select = State()
    confirm = State()
