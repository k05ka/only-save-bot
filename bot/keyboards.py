from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Optional

class CallbackFactory(CallbackData, prefix='probefab'):
    action: str
    value: Optional[int] = None
    str_value: Optional[str] = None

def video_res_fab(res):
    builder = InlineKeyboardBuilder()
    if res:
        for r in res.keys():
            if r == '1080p':
                builder.button(text='Full HD', callback_data=CallbackFactory(action='choose_resolution', str_value='1080p'))
            elif r == '1440p':
                builder.button(text='QHD', callback_data=CallbackFactory(action='technical_banner', str_value='1440p'))
            elif r == '2160p':
                builder.button(text='4K', callback_data=CallbackFactory(action='technical_banner', str_value='2160p'))
            else:
                builder.button(text=r, callback_data=CallbackFactory(action='choose_resolution', str_value=r))
    builder.button(text='🔄 Reset', callback_data=CallbackFactory(action='reset'))
    builder.adjust(3)
    return builder.as_markup()