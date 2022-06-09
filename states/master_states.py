from aiogram.dispatcher.filters.state import State, StatesGroup


class MasterTimetable(StatesGroup):
    day_selected = State()
    time_selected = State()
    cancellation_selected = State()
    book_selected = State()
    confirm_selected = State()
    customer_name_typed = State()


class UpdateProfileInfo(StatesGroup):
    info_typed = State()


class UploadProfilePhoto(StatesGroup):
    photo_selected = State()


class UploadPortfolioPhoto(StatesGroup):
    photo_selected = State()
