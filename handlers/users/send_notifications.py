import logging
from asyncio import sleep

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.exceptions import ChatNotFound

from filters import IsAdmin
from keyboards.default import kb_recipients, kb_admin_commands
from keyboards.inline import kb_inform_confirm
from loader import bot, dp
from states import SendNotification
from utils.db_api.models import Customer, Master


@dp.message_handler(IsAdmin(), text=['Send notification', '/inform'], state='*')
async def set_recipients(message: Message, state: FSMContext = None):
    if state is not None:
        await state.finish()
    await message.answer('Select recipients', reply_markup=kb_recipients)
    await SendNotification.recipients.set()


@dp.message_handler(text=['Inform masters', 'Inform customers', 'Inform both masters and customers'],
                    state=SendNotification.recipients)
async def set_notification(message: Message, state: FSMContext):
    await state.update_data(recipients=message.text)
    await message.answer(text='Enter the text of the notification\n\n'
                              '<em>HINT: can not be a command</em>',
                         reply_markup=ReplyKeyboardRemove())
    await SendNotification.notification.set()


@dp.message_handler(regexp=r'^[^\/].+$', state=SendNotification.notification)
async def check_notification(message: Message, state: FSMContext):
    await state.update_data(notification=message.text)
    await message.answer(text='Your notification is:\n\n'
                              f'<em><b>"{message.text}"</b></em>\n\n'
                              'Send this notification?',
                         reply_markup=kb_inform_confirm)
    await SendNotification.confirm.set()


@dp.callback_query_handler(text_contains='change', state=SendNotification.confirm)
async def change_notification(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup()
    await call.message.answer('Please, re-enter the text of the notification')
    await SendNotification.notification.set()


@dp.callback_query_handler(text_contains='confirm', state=SendNotification.confirm)
async def confirm_notification(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    data = await state.get_data()
    masters = await Master.query.gino.all()
    customers = await Customer.query.gino.all()
    if data['recipients'] == 'Inform masters':
        recipients = masters
    elif data['recipients'] == 'Inform customers':
        recipients = customers
    else:
        recipients = (masters + customers)
    for recipient in recipients:
        try:
            await bot.send_message(chat_id=recipient.chat_id,
                                   text='<b>Notification from administrator:</b>\n\n'
                                        f'<em>"{data["notification"]}"</em>\n\n'
                                        'Wish you a good day!')
            await sleep(0.3)
        except ChatNotFound:
            logging.info(f'ChatNotFound: chat id - {recipient.chat_id}')
            await call.message.answer(
                f'<b>Alert:</b>\n\n'
                f'Notification has not been to <b>{recipient.name}</b>, phone number: <b>{recipient.phone}</b>'
            )
    await call.message.answer('Main menu, choose one of the available commands 👇', reply_markup=kb_admin_commands)
    await state.finish()
