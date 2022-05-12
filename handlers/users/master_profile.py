from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.default import kb_master_commands, kb_master_profile
from loader import dp
from states import UpdateProfileInfo, UploadProfilePhoto
from utils.db_api.models import Master


@dp.message_handler(text=['My profile', '/profile'])
async def master_profile(message: Message):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    text = f'<b>Name:</b> {master.name}\n' \
           f'<b>Phone number:</b> {master.phone}\n' \
           f'<b>Info:</b> {master.info}'
    if master.photo_id:
        await message.answer_photo(photo=master.photo_id, caption=text, reply_markup=kb_master_profile)
    else:
        await message.answer(text=text, reply_markup=kb_master_profile)


@dp.message_handler(text=['Update profile info', '/update_info'])
async def set_info(message: Message):
    await message.answer('Enter the text of the info', reply_markup=ReplyKeyboardRemove())
    await UpdateProfileInfo.info.set()


@dp.message_handler(state=UpdateProfileInfo.info)
async def update_info(message: Message, state: FSMContext):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await master.update(info=message.text).apply()
    await message.answer('Profile info has been successfully updated', reply_markup=kb_master_commands)
    await state.finish()


@dp.message_handler(text=['Upload profile photo', '/upload_photo'])
async def set_photo(message: Message):
    await message.answer('Send your photo', reply_markup=ReplyKeyboardRemove())
    await UploadProfilePhoto.photo.set()


@dp.message_handler(content_types=['photo'], state=UploadProfilePhoto.photo)
async def upload_photo(message: Message, state: FSMContext):
    master = await Master.query.where(Master.chat_id == message.from_user.id).gino.first()
    await master.update(photo_id=message.photo[-1].file_id).apply()
    await message.answer('Profile photo has been successfully uploaded', reply_markup=kb_master_commands)
    await state.finish()
