from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    image = State()
    name = State()
    author = State()
    genre = State()
    translator = State()
    page = State()
    cover = State()
    description = State()
    category = State()
    price = State()
    phone_number = State()
    book_id = State()
    username = State()
    user_id = State()
    idsi = State()


