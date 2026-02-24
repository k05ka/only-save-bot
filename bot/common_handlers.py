from aiogram import Router, types, F
from aiogram.filters import CommandStart, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from fluent.runtime import FluentLocalization
import re
from download_engine import catch_video

common_router = Router()

class LinkFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
        return bool(re.search(pattern, message.text))

@common_router.message(CommandStart())
async def cmd_start(
    event: types.Message, 
    state: FSMContext, 
    l10n: FluentLocalization
    ):
    await event.answer(text=l10n.format_value('welcome-text'))
    await state.clear()

@common_router.message(
    F.text.lower().contains('youtube.com') | 
    F.text.lower().contains('youtu.be')
)
async def message_with_link(
    event: types.Message, 
    state: FSMContext, 
    l10n: FluentLocalization
    ):
    if catch_video(url=event.text):
        await event.answer(l10n.format_value('message-with-link'))
    else:
        await event.answer(l10n.format_value('message-bad-link'))

@common_router.message(F)  
async def unrecognized_message(
    event: types.Message, 
    state: FSMContext, 
    l10n: FluentLocalization
    ):
    await event.answer(text=l10n.format_value('other-messages'))
