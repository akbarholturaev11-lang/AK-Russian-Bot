from aiogram.fsm.state import State, StatesGroup


class FeedbackStates(StatesGroup):
    waiting_other_text = State()
    waiting_dislike_detail = State()
    waiting_admin_reply = State()
