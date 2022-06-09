import logging
from asyncio import sleep

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.exceptions import ChatNotFound

from data.messages import get_message
from filters import IsAdmin
from keyboards.default.kb_admin import kb_recipients, kb_admin_commands
from keyboards.inline.kb_inline_admin import kb_inform_confirm
from loader import bot, dp
from states.admin_states import SendNotification
from utils.db_api.models import Customer, Master


@dp.message_handler(IsAdmin(), text=["Send notification", "/inform"], state="*")
async def set_recipients(message: Message, state: FSMContext = None):
    if state:
        await state.finish()
    await message.answer(
        text=get_message("select_recipients"), reply_markup=kb_recipients
    )
    await SendNotification.recipients_selected.set()


@dp.message_handler(
    text=["Inform masters", "Inform customers", "Inform both masters and customers"],
    state=SendNotification.recipients_selected,
)
async def set_notification(message: Message, state: FSMContext):
    await state.update_data(recipients=message.text)
    await message.answer(
        text=get_message("set_notification"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await SendNotification.notification_typed.set()


@dp.message_handler(regexp=r"^[^\/].+$", state=SendNotification.notification_typed)
async def check_notification(message: Message, state: FSMContext):
    await state.update_data(notification=message.text)
    await message.answer(
        text=get_message("check_notification").format(message.text),
        reply_markup=kb_inform_confirm,
    )
    await SendNotification.confirm_selected.set()


@dp.callback_query_handler(text_contains="change", state=SendNotification.confirm_selected)
async def change_notification(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup()
    await call.message.answer(text=get_message("change_notification"))
    await SendNotification.notification_typed.set()


@dp.callback_query_handler(text_contains="confirm", state=SendNotification.confirm_selected)
async def confirm_notification(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    data = await state.get_data()
    masters = await Master.filter(is_active=True)
    customers = await Customer.all()
    if data["recipients"] == "Inform masters":
        recipients = masters
    elif data["recipients"] == "Inform customers":
        recipients = customers
    else:
        recipients = masters + customers
    for recipient in recipients:
        try:
            await bot.send_message(
                chat_id=recipient.chat_id,
                text=get_message("admin_notification").format(data["notification"]),
            )
            await sleep(0.3)
        except ChatNotFound:
            logging.info(f"ChatNotFound: chat id - {recipient.chat_id}")
            await call.message.answer(
                text=get_message("alert_no_recipient_chat_id").format(
                    recipient.name, recipient.phone
                )
            )
    await call.message.answer(
        text=get_message("menu"),
        reply_markup=kb_admin_commands,
    )
    await state.finish()
