from aiogram.fsm.state import State, StatesGroup


class AdminPortfolioStates(StatesGroup):
    waiting_amount = State()
    waiting_reason = State()
