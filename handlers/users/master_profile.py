from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from keyboards.default import kb_master_commands, kb_master_profile
from keyboards.inline import kb_portfolio_photo
from loader import dp
from states import UpdateProfileInfo, UploadProfilePhoto, UploadPortfolioPhoto
from utils.db_api.models import Master, PortfolioPhoto


@dp.message_handler(text=['My profile', '/profile'], state='*')
async def master_profile(message: Message, state: FSMContext = None):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    text = f'<b>Name:</b> {master.name}\n' \
           f'<b>Phone number:</b> {master.phone}\n' \
           f'<b>Info:</b> {master.info}'
    if master.photo_id:
        await message.answer_photo(photo=master.photo_id, caption=text, reply_markup=kb_master_profile)
    else:
        await message.answer(text=text, reply_markup=kb_master_profile)
    if state is not None:
        await state.finish()


@dp.message_handler(text=['Update profile info', '/update_info'], state='*')
async def set_info(message: Message, state: FSMContext = None):
    await message.answer('Enter the text of the info\n\n'
                         '<em>HINT: up to 200 characters</em>', reply_markup=ReplyKeyboardRemove())
    if state is not None:
        await state.finish()
    await UpdateProfileInfo.info.set()


@dp.message_handler(regexp=r'^[^\/].{1,200}$', state=UpdateProfileInfo.info)
async def update_info(message: Message, state: FSMContext):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await master.update(info=message.text).apply()
    await message.answer('Profile info has been successfully updated', reply_markup=kb_master_commands)
    await state.finish()


@dp.message_handler(text=['Upload profile photo', '/profile_photo'], state='*')
async def set_photo(message: Message, state: FSMContext = None):
    await message.answer('Attach a photo and send it\n\n'
                         '<em>HINT: takes only one photo</em>', reply_markup=ReplyKeyboardRemove())
    if state is not None:
        await state.finish()
    await UploadProfilePhoto.photo.set()


@dp.message_handler(content_types=['photo'], state=UploadProfilePhoto.photo)
async def upload_photo(message: Message, state: FSMContext):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await master.update(photo_id=message.photo[-1].file_id).apply()
    await message.answer_photo(photo=message.photo[-1].file_id,
                               caption='Profile photo has been successfully uploaded',
                               reply_markup=kb_master_commands)
    await state.finish()


@dp.message_handler(text=['Upload portfolio photo', '/portfolio_photo'], state='*')
async def set_portfolio_photo(message: Message, state: FSMContext = None):
    await message.answer('Attach a photo and send it\n\n'
                         '<em>HINT: takes only one photo</em>', reply_markup=ReplyKeyboardRemove())
    if state is not None:
        await state.finish()
    await UploadPortfolioPhoto.photo.set()


@dp.message_handler(content_types=['photo'], state=UploadPortfolioPhoto.photo)
async def upload_portfolio_photo(message: Message, state: FSMContext):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await PortfolioPhoto.create(master_id=master.id, photo_id=message.photo[-1].file_id)
    await message.answer_photo(photo=message.photo[-1].file_id,
                               caption='Photo has been successfully added to your portfolio',
                               reply_markup=kb_portfolio_photo)
    await state.finish()


@dp.callback_query_handler(text_contains='one_more')
async def upload_one_more_portfolio_photo(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup()
    await call.message.answer('Attach a photo and send it\n\n'
                              '<em>HINT: takes only one photo</em>')
    await UploadPortfolioPhoto.photo.set()


@dp.callback_query_handler(text_contains='main_menu')
async def back_to_main_menu(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup()
    await call.message.answer('Main menu:', reply_markup=kb_master_commands)
