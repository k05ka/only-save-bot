import logging
from functools import wraps
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router, types, Bot
from bot.config import BotConfig
from keyboards import *
from fluent.runtime import FluentLocalization


support_router = Router()
logging.basicConfig(level=logging.INFO)


def admin_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        config = kwargs.get("config")
        if config and str(message.from_user.id) in config.admin_id:
            return await func(message, *args, **kwargs)
        else:
            await message.answer("You don't have permissions for this action.")
    return wrapper



@support_router.message(Command("reply"))
@admin_only
async def cmd_reply_support_question(
    message: types.Message,
    bot: Bot, 
    config: BotConfig, 
    l10n: FluentLocalization
):
    try:
        args = message.text.split(maxsplit=3)[1:]
        user_id = str(args[0])
        original_message_id = str(args[1])
        reply_message = args[2]
        reply_text = l10n.format_value('support-answer', {'message-text': reply_message})

        await bot.send_message(
            chat_id=user_id,
            text=reply_text,
            reply_to_message_id=original_message_id, reply_markup=get_continue_support_fab()
        )

        await message.answer("✅ Ответ отправлен!")

    except ValueError:
        await message.answer("❌ Неверный формат ID")
    except Exception as e:
        await message.answer(f"🚫 Ошибка: {str(e)}")