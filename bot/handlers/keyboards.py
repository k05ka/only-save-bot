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


def complete_fab():
    builder = InlineKeyboardBuilder()
    builder.button(text='🏁 Отлично', callback_data=CallbackFactory(action='finish'))
    builder.button(text='🫶 Поблагодарить', callback_data=CallbackFactory(action='donate'))
    builder.adjust(2)
    return builder.as_markup()


def get_support_fab():
    builder = InlineKeyboardBuilder()
    builder.button(text="✉️ Задать вопрос", callback_data=CallbackFactory(action="support_chat"))
    builder.button(text='🏁 На главную', callback_data=CallbackFactory(action='on_main'))
    builder.adjust(2)
    return builder.as_markup()


def get_continue_support_fab():
    builder = InlineKeyboardBuilder()
    builder.button(text="✉️Написать сообщение", callback_data=CallbackFactory(action='continue_support_chat'))
    builder.button(text='❎ Закрыть вопрос', callback_data=CallbackFactory(action='on_main'))
    builder.adjust(1)
    return builder.as_markup()