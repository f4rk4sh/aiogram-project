from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from data.messages import get_message
from filters import IsMaster
from keyboards.default import kb_master_commands, kb_master_profile
from keyboards.inline import kb_portfolio_photo
from loader import dp
from states import UpdateProfileInfo, UploadPortfolioPhoto, UploadProfilePhoto
from utils.db_api.models import Master, PortfolioPhoto


@dp.message_handler(IsMaster(), text=["My profile", "/profile"], state="*")
async def master_profile(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    master = await Master.get(chat_id=message.from_user.id)
    if master.photo_id:
        await message.answer_photo(
            photo=master.photo_id,
            caption=get_message("master_profile").format(
                master.name, master.phone, master.info
            ),
            reply_markup=kb_master_profile,
        )
    else:
        await message.answer(
            text=get_message("master_profile").format(
                master.name, master.phone, master.info
            ),
            reply_markup=kb_master_profile,
        )


@dp.message_handler(IsMaster(), text=["Update profile info", "/update_info"], state="*")
async def set_info(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    await message.answer(
        text=get_message("set_info"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await UpdateProfileInfo.info.set()


@dp.message_handler(regexp=r"^[^\/].{1,200}$", state=UpdateProfileInfo.info)
async def update_info(message: Message, state: FSMContext):
    master = await Master.get(chat_id=message.from_user.id)
    master.info = message.text
    await master.save()
    await message.answer(
        text=get_message("profile_update_success"), reply_markup=kb_master_commands
    )
    await state.finish()


@dp.message_handler(
    IsMaster(), text=["Upload profile photo", "/profile_photo"], state="*"
)
async def set_photo(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    await message.answer(
        text=get_message("set_photo"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await UploadProfilePhoto.photo.set()


@dp.message_handler(content_types=["photo"], state=UploadProfilePhoto.photo)
async def upload_photo(message: Message, state: FSMContext):
    master = await Master.get(chat_id=message.from_user.id)
    master.photo_id = message.photo[-1].file_id
    await master.save()
    await message.answer_photo(
        photo=message.photo[-1].file_id,
        caption=get_message("profile_photo_update_success"),
        reply_markup=kb_master_commands,
    )
    await state.finish()


@dp.message_handler(
    IsMaster(), text=["Upload portfolio photo", "/portfolio_photo"], state="*"
)
async def set_portfolio_photo(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    await message.answer(
        text=get_message("set_photo"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await UploadPortfolioPhoto.photo.set()


@dp.message_handler(content_types=["photo"], state=UploadPortfolioPhoto.photo)
async def upload_portfolio_photo(message: Message, state: FSMContext):
    master = await Master.get(chat_id=message.from_user.id)
    await PortfolioPhoto.create(master=master, photo_id=message.photo[-1].file_id)
    await message.answer_photo(
        photo=message.photo[-1].file_id,
        caption=get_message("portfolio_photo_upload_success"),
        reply_markup=kb_portfolio_photo,
    )
    await state.finish()


@dp.callback_query_handler(text_contains="one_more")
async def upload_one_more_portfolio_photo(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup()
    await call.message.answer(text=get_message("set_photo"))
    await UploadPortfolioPhoto.photo.set()


@dp.callback_query_handler(text_contains="main_menu")
async def back_to_main_menu(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup()
    await call.message.answer(text=get_message("menu"), reply_markup=kb_master_commands)
