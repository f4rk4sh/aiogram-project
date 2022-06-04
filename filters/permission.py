from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from data.config import ADMINS
from utils.db_api.models import Master


class IsAdmin(BoundFilter):
    async def check(self, message: Message) -> bool:
        return message.from_user.id in ADMINS


class IsMaster(BoundFilter):
    async def check(self, message: Message) -> bool:
        return int(message.from_user.id) in [
            master.chat_id for master in await Master.all() if master.is_active
        ]
