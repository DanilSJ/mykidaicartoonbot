from aiogram.fsm.state import State, StatesGroup


class Video(StatesGroup):
    image = State()
    prompt = State()
    audio = State()
    duration = State()
