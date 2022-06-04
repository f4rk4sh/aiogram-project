from aiogram.types import BotCommand


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            BotCommand("menu", "Main menu"),
            BotCommand("help", "View help information"),
        ]
    )
