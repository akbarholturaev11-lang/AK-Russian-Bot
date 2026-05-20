from aiogram.fsm.state import State, StatesGroup


class AdminPriceStates(StatesGroup):
    waiting_amount = State()


class AdminRequiredChannelStates(StatesGroup):
    waiting_channel = State()
