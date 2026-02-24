from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from pathlib import Path
import os


def load_config():
    possible_paths = [
        Path('.') / '.env',
        Path('..') / '.env',
    ]
    for path in possible_paths:
        if path.exists():
            load_dotenv(dotenv_path=path)
            return True
    return False

load_config()


class BotConfig:
    """
    Configuration class for the bot.
    """
    def __init__(self, admin_id: list, welcome_message: str) -> None:
        """
        Initialize the BotConfig instance.

        :param admin_id: List of admin IDs.
        :param welcome_message: Welcome message for users.
        """
        self.admin_id = admin_id
        self.welcome_message = welcome_message

# Initialize the bot with the provided token and HTML parse mode
save_bot = Bot(
    token= os.getenv('TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Initialize the dispatcher with memory storage and user-in-chat FSM strategy
save_dp = Dispatcher(
    storage=MemoryStorage(),
    fsm_strategy=FSMStrategy.USER_IN_CHAT
)

# Set bot configuration and API client in the dispatcher
save_dp["config"] = BotConfig(
    admin_id=os.getenv('admin_ids').split(','),
    welcome_message=(
        "Добро пожаловать! \
        Это тестовый бот для скачивания видео с YouTube. Чтобы воспользоваться ботом, отправь ссылку нужного видео  сообщением 👇🏿👇🏿👇🏿"
    ),
)