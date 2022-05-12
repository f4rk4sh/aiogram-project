from aiogram.dispatcher.filters.state import StatesGroup, State


class UpdateProfileInfo(StatesGroup):
    info = State()


class UploadProfilePhoto(StatesGroup):
    photo = State()
