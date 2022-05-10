import logging
from asyncio import sleep

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from keyboards.default import kb_recipients, kb_admin_commands
from keyboards.inline import kb_inform_confirm
from loader import bot, dp
from states import Inform
from utils.db_api.models import Customer, Master


@dp.message_handler(text='Inform')
async def set_recipients(message: Message):
    await message.answer('Select recipients', reply_markup=kb_recipients)
    await Inform.recipients.set()


@dp.message_handler(text=['Inform masters', 'Inform customers', 'Inform both masters and customers'], state=Inform.recipients)
async def set_notification(message: Message, state: FSMContext):
    await state.update_data(recipients=message.text)
    await message.answer('Enter the text of the notification', reply_markup=ReplyKeyboardRemove())
    await Inform.notification.set()


@dp.message_handler(state=Inform.notification)
async def check_notification(message: Message, state: FSMContext):
    await state.update_data(notification=message.text)
    await message.answer('Your notification is:\n\n'
                         f'<em><b>"{message.text}"</b></em>\n\n'
                         'Send this notification?', reply_markup=kb_inform_confirm)
    await Inform.confirm.set()


@dp.callback_query_handler(text_contains='change', state=Inform.confirm)
async def change_notification(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer('Please, re-enter the text of the notification')
    await Inform.notification.set()


@dp.callback_query_handler(text_contains='confirm', state=Inform.confirm)
async def confirm_notification(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    notification = data.get('notification')
    recipients = data.get('recipients')
    masters = await Master.query.gino.all()
    customers = await Customer.query.gino.all()
    if recipients == 'Inform masters':
        recipients = masters
    elif recipients == 'Inform customers':
        recipients = customers
    else:
        recipients = (masters + customers)
    for recipient in recipients:
        try:
            await bot.send_message(chat_id=recipient.chat_id, text=notification)
            await sleep(0.3)
        except Exception:
            logging.info(f'Notification has not been sent to {recipient.name}, chat id: {recipient.chat_id}')
    await call.message.answer('Notification has been successfully sent', reply_markup=kb_admin_commands)
    await state.reset_state()
