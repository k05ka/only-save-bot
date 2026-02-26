from aiogram import Router, types, F
from aiogram.filters import CommandStart, BaseFilter, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from fluent.runtime import FluentLocalization
import re
from .keyboards import *
from .states import *
from download_engine import catch_video, compile_available_streams, download_video, cleanup_temp_files

common_router = Router()

@common_router.message(CommandStart())
async def cmd_start(
    event: types.Message, 
    state: FSMContext, 
    l10n: FluentLocalization
    ):
    await event.answer(text=l10n.format_value('welcome-text'))
    await state.clear()

@common_router.message(Command(commands='info'))
async def cmd_info(
    event: types.Message, 
    state: FSMContext, 
    l10n: FluentLocalization
    ):
    await event.answer(text=l10n.format_value('info-text'))
    await state.clear()


@common_router.callback_query(CallbackFactory.filter(F.action == 'reset'))
async def cmd_reset(
    event: types.CallbackQuery,
    state: FSMContext, 
    l10n: FluentLocalization   
):
    await state.clear()
    await event.message.answer(text=l10n.format_value('reset-banner'))
    await event.answer()

@common_router.callback_query(CallbackFactory.filter(F.action == 'finish'))
async def cmd_reset(
    event: types.CallbackQuery,
    state: FSMContext, 
    l10n: FluentLocalization   
):
    await state.clear()
    await event.message.answer(text=l10n.format_value('finish-banner'))
    await event.answer()

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
        result = compile_available_streams(url=event.text)
        await state.update_data(
            url = event.text,
            video_title=result.get('title'),
            streams=result.get('resolutions')
        )
        keyboard = video_res_fab(res=result.get('resolutions'))
        await event.answer(
            text=l10n.format_value('choose-video-res', {'title': result.get('title')}), 
            reply_markup=keyboard
        )
        await state.set_state(ChatForm.choose_vide_res)
    else:
        await event.answer(l10n.format_value('message-bad-link'))

@common_router.callback_query(CallbackFactory.filter(F.action == 'choose_resolution'), StateFilter(ChatForm.choose_vide_res))
async def callback_send_video(
    callback: types.CallbackQuery,
    callback_data: CallbackFactory,
    state: FSMContext,
    l10n: FluentLocalization,
):
    data = await state.get_data()
    streams = data.get('streams')
    selected_resolution = callback_data.str_value
    selected_stream = streams.get(selected_resolution)
    
    progress_message = await callback.message.answer(
        l10n.format_value('downloading-video', {'resolution': selected_resolution})
    )
    await callback.message.delete()
    await callback.answer()
    try:
        video_path, width, height = await download_video(selected_stream, callback.from_user.id, data.get('url'))
        
        await progress_message.edit_text(
            l10n.format_value('sending-video', {'resolution': selected_resolution})
        )

        await callback.message.answer_video(
            reply_markup=complete_fab(),
            video=types.FSInputFile(video_path),
            width=width, height=height, supports_streaming=True,
            caption=l10n.format_value('video-ready', {
                'title': data.get('video_title'),
                'resolution': selected_resolution
            }), 
        )
        
        await progress_message.delete()
        await state.clear()
        cleanup_temp_files()
            
    except Exception as e:
        await progress_message.edit_text(
            l10n.format_value('error-downloading', {'error': str(e)})
        )
        await state.clear()

# @common_router.message(F)  
# async def unrecognized_message(
#     event: types.Message, 
#     state: FSMContext,
#     l10n: FluentLocalization
#     ):
#     await event.answer(text=l10n.format_value('other-messages'))
#     await state.clear()