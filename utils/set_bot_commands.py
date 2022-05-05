from aiogram.types import BotCommand


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand('start', 'Start up a bot'),
        BotCommand('help', 'See help information'),
        BotCommand('cancel', 'Cancel the current operation')
    ])
