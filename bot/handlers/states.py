from aiogram.fsm.state import State, StatesGroup


class ChatForm(StatesGroup):
    choose_vide_res = State()
    reset_chat = State()
    donate = State()
    donate_success = State()
    choose_star = State()
    call_support = State()
    