from aiogram.fsm.state import State, StatesGroup


class AdCampaignStates(StatesGroup):
    waiting_title = State()
    waiting_content = State()
    waiting_custom_duration = State()
    waiting_send_count = State()
    waiting_start_at = State()
