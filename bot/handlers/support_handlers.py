import logging
from functools import wraps
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram import Router, types, Bot, F
from bot.config import BotConfig
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fluent.runtime import FluentLocalization
from .states import *
from .keyboards import *


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

@support_router.message(Command("support"))
@support_router.callback_query(CallbackFactory.filter(F.action == 'continue_support_chat'))
async def wait_support_question(
    event: types.Message,
    l10n: FluentLocalization,
    state: FSMContext,
):
    await state.set_state(ChatForm.call_support)
    await event.answer(text='✍️ Напишите сообщение администратору')

@support_router.message(StateFilter(ChatForm.call_support))
async def send_to_admin(
    message: types.Message,
    state: FSMContext,
    l10n: FluentLocalization,
    bot: Bot,
    config: BotConfig
):
    user_message = message.text
    text = l10n.format_value("admin-support-mesage", {'tg-id': str(message.from_user.id),
                                                      'message-id': str(message.message_id), 
                                                      'user-message': user_message})
    for admin in config.admin_id:
        await bot.send_message(chat_id=admin, text=text)
    await message.answer(text='📨 Отправлено администратору')
    await state.clear()

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