import logging
import asyncio
from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from bot.config import save_bot, save_dp, BotConfig
from bot.handlers.common_handlers import common_router
from bot.handlers.stars_handlers import stars_router
from bot.handlers.support_handlers import support_router
from bot.middlewares import L10nMiddleware
from bot.fluent_loader import get_fluent_localization

# Enable console logging
logging.basicConfig(level=logging.INFO)

# Register function for including custom handlers
def register_routes(dp: Dispatcher) -> None:
    """
    Register routers for the dispatcher.
    """
    dp.include_router(common_router)
    dp.include_router(stars_router)
    dp.include_router(support_router)

# Compile the bot's menu commands
async def set_commands():
    """
    Set bot commands for the menu.
    """
    commands = [
        BotCommand(command='start', description='🏁 В начало'),
        BotCommand(command='info', description='🆔 Информация'),
        BotCommand(command='donate', description='⭐️ Поддержать проект'),
        BotCommand(command='support', description='🛟 Помощь'),
    ]
    await save_bot.set_my_commands(commands, BotCommandScopeDefault())

# Send a message to admins when the bot starts
async def start_bot(config: BotConfig):
    """
    Send a message to admins when the bot starts.
    """
    await set_commands()
    try:
        for admin in config.admin_id:
            await save_bot.send_message(admin, 'Bot is started')
    except Exception as e:
        logging.error(f"Failed to notify admins on startup: {e}")

# Send a message to admins when the bot stops
async def stop_bot(config: BotConfig):
    """
    Send a message to admins when the bot stops.
    """
    try:
        for admin in config.admin_id:
            await save_bot.send_message(admin, 'Bot is stopped')
    except Exception as e:
        logging.error(f"Failed to notify admins on shutdown: {e}")

# Main function to run the bot
async def main() -> None:
    """
    Main function to start the bot.
    """
    locale = get_fluent_localization()
    dp = save_dp
    register_routes(dp)

    # Register startup and shutdown events
    dp.message.outer_middleware(L10nMiddleware(locale))
    dp.callback_query.outer_middleware(L10nMiddleware(locale))
    dp.pre_checkout_query.outer_middleware(L10nMiddleware(locale))
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        # Delete the webhook and start polling
        await save_bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(save_bot)
    finally:
        # Close the bot session
        await save_bot.session.close()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())