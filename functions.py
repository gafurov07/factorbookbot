from aiogram.types import KeyboardButton, InlineKeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from sqlalchemy import Select
from sqlalchemy.dialects.postgresql import Insert

from database import engine, Book, Basket, Order


async def home_buttons():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text='📚 Kitoblar'), KeyboardButton(text='📃 Mening buyurtmalarim'),
            KeyboardButton(text='🔵 Biz ijtimoiy tarmoqlarda'), KeyboardButton(text="📞 Biz bilan bog'lanish"))
    rkb.adjust(1, 1, 2)
    return rkb


async def inlines(names: list, type='a'):
    if type == 'category':
        ikb = InlineKeyboardBuilder()
        for i in names:
            if i == "⚡️IKAR":
                ikb.add(InlineKeyboardButton(text=i, callback_data=i))
                continue
            elif i == '🔍 Qidirish':
                ikb.add(InlineKeyboardButton(text=i, switch_inline_query_current_chat=""))
                continue
            ikb.add(InlineKeyboardButton(text=i, callback_data=f"{i}_category"))
        ikb.adjust(2)
        return ikb
    ikb = InlineKeyboardBuilder()
    for i in names:
        ikb.add(InlineKeyboardButton(text=i, callback_data=f"{i}_book"))
    ikb.add(InlineKeyboardButton(text="◀️ Orqaga", callback_data="back"))
    ikb.adjust(2)
    return ikb
    # await message.answer(text=text, reply_markup=ikb.as_markup())


async def text(data):
    if type(data) == dict:
        text = f'''🔹 Nomi: {data['name']}
Muallifi; {data['author']}
Janri; {data['genre']}
Tarjimon; {data['translator']}
Bet; {data['page']}
Muqova; {data['cover']}
Kitob haqida; {data['description']}
💸 Narxi: {data['price']} so'm'''
        return text
    else:
        text = f'''🔹 Nomi: {data[1]}
Muallifi; {data[2]}
Janri; {data[3]}
Tarjimon; {data[4]}
Bet; {data[5]}
Muqova; {data[6]}
Kitob haqida; {data[7]}
💸 Narxi: {data[9]} so'm'''
        return text


async def insert(data, name='Book'):
    if name == 'Book':
        with engine.connect() as conn:
            query = Insert(Book).values([*data.values()])
            conn.execute(query)
            conn.commit()
        return
    elif name == 'order':
        with engine.connect() as conn:
            query = Insert(Order).values([*data])
            conn.execute(query)
            conn.commit()
        return
    with engine.connect() as conn:
        query = Insert(Basket).values([*data])
        conn.execute(query)
        conn.commit()


async def message_inline(_c):
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text="➖", callback_data='kamayish'),
            InlineKeyboardButton(text=f"{_c}", callback_data='num'),
            InlineKeyboardButton(text="➕", callback_data='kopayish'),
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back"),
            InlineKeyboardButton(text="🛒 Savatga qo'shish", callback_data="savatga_qoshish"))
    ikb.adjust(3, 2)
    return ikb


async def _select(cls, **kwargs):
    conn = engine.connect()
    return conn.execute(Select(cls).where(**kwargs))

