from aiogram.dispatcher.filters.state import State, StatesGroup


class UpdateProfileInfo(StatesGroup):
    info = State()


class UploadProfilePhoto(StatesGroup):
    photo = State()


class UploadPortfolioPhoto(StatesGroup):
    photo = State()
