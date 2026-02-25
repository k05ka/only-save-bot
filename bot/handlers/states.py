from aiogram.fsm.state import State, StatesGroup


class ChatForm(StatesGroup):
    choose_vide_res = State()
    reset_chat = State()
    donate = State()