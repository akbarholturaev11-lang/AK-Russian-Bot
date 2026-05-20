from aiogram.fsm.state import State, StatesGroup


class AdminAudioStates(StatesGroup):
    waiting_for_audio = State()
