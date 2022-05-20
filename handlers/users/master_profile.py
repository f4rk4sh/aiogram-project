from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.default import kb_master_commands, kb_master_profile
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
    await message.answer('Enter the text of the info', reply_markup=ReplyKeyboardRemove())
    if state is not None:
        await state.finish()
    await UpdateProfileInfo.info.set()


@dp.message_handler(state=UpdateProfileInfo.info)
async def update_info(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await message.answer('You can not use command as the text of your profile info\n'
                             'Re-enter the text of the info')
        await UpdateProfileInfo.info.set()
    else:
        master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
        await master.update(info=message.text).apply()
        await message.answer('Profile info has been successfully updated', reply_markup=kb_master_commands)
        await state.finish()


@dp.message_handler(text=['Upload profile photo', '/upload_photo'], state='*')
async def set_photo(message: Message, state: FSMContext = None):
    await message.answer('Send your photo', reply_markup=ReplyKeyboardRemove())
    if state is not None:
        await state.finish()
    await UploadProfilePhoto.photo.set()


@dp.message_handler(content_types=['photo'], state=UploadProfilePhoto.photo)
async def upload_photo(message: Message, state: FSMContext):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await master.update(photo_id=message.photo[-1].file_id).apply()
    await message.answer('Profile photo has been successfully uploaded', reply_markup=kb_master_commands)
    await state.finish()


@dp.message_handler(text=['Upload portfolio photo', '/upload_portfolio_photo'], state='*')
async def set_portfolio_photo(message: Message, state: FSMContext = None):
    await message.answer('Send your photo', reply_markup=ReplyKeyboardRemove())
    if state is not None:
        await state.finish()
    await UploadPortfolioPhoto.photo.set()


@dp.message_handler(content_types=['photo'], state=UploadPortfolioPhoto.photo)
async def upload_portfolio_photo(message: Message, state: FSMContext):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await PortfolioPhoto.create(master_id=master.id, photo_id=message.photo[-1].file_id)
    await message.answer('Photo has been successfully added to your portfolio', reply_markup=kb_master_commands)
    await state.finish()
