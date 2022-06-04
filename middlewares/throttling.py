import asyncio
from typing import Union

from aiogram import Dispatcher
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=5, key_prefix="antiflood_"):
        self.limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def throttle(self, target: Union[Message, CallbackQuery]):
        handler = current_handler.get()
        if not handler:
            return
        dp = Dispatcher.get_current()
        limit = getattr(handler, "throttling_rate_limit", self.limit)
        key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        try:
            await dp.throttle(key, rate=limit)
        except Throttled as t:
            await self.target_throttled(target, t, dp, key)
            raise CancelHandler()

    @staticmethod
    async def target_throttled(
        target: Union[Message, CallbackQuery],
        throttled: Throttled,
        dispatcher: Dispatcher,
        key: str,
    ):
        message = target.message if isinstance(target, CallbackQuery) else target
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count == 2:
            await message.reply(
                f"Too many requests!\n" f"This command is locked for {delta:.1f} sec."
            )
            return
        await asyncio.sleep(delta)
        thr = await dispatcher.check_key(key)
        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply(f"This command is now available")

    async def on_process_message(self, message: Message, data: dict):
        await self.throttle(message)

    # async def on_process_callback_query(self, call: CallbackQuery, data: dict):
    #     await self.throttle(call)
