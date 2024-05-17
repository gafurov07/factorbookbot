import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, KeyboardButton, InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle, BotCommand, BotCommandScopeChat
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy import Select, Delete

from database import engine, Book, Basket, Order, Category
from forms import Form
from functions import home_buttons, inlines, text, insert, message_inline, _select

# TOKEN = getenv("BOT_TOKEN")
TOKEN = '6686631791:AAEyAR75prxhDQqOjYoKm6wIGJr9XDfXGKk'
order_book_list = []
admins = [5760868166]
dp = Dispatcher()
_c = 0


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(user_id=message.from_user.id)
    rkb = await home_buttons()
    await message.answer(text="Assalomu alaykum! Tanlang.", reply_markup=rkb.as_markup(resize_keyboard=True))


@dp.message(F.text == '📚 Kitoblar')
async def books(message: Message):
    _names = await _select(Category.name)
    print(_names, 123)
    ikb = await inlines(names=_names, type="category")
    res = await _select(Basket)
    count_basket = [i for i in res]
    if len(count_basket):
        ikb.row(InlineKeyboardButton(text=f"🛒 Savat ({len(count_basket)})", callback_data="savatni_och"))
    await message.answer(text="Kategoriyalardan birini tanlang", reply_markup=ikb.as_markup())


@dp.message(Command('add'), F.from_user.id.in_(admins))
async def state_image(message: Message, state: FSMContext):
    await message.answer("Kitobning rasmini URLni kiriting")
    await state.set_state(Form.image)


@dp.message(Form.image)
async def state_image_update(message: Message, state: FSMContext):
    await state.update_data(image=message.text)
    await message.answer("Kitobning nomini kiriting")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Kitobning muallifini F.I.O sini kiriting")
    await state.set_state(Form.author)


@dp.message(Form.author)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.answer("Kitobning janirini kiriting")
    await state.set_state(Form.genre)


@dp.message(Form.genre)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await message.answer("Kitobning tarjimonining F.I.O sini kiriting")
    await state.set_state(Form.translator)


@dp.message(Form.translator)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(translator=message.text)
    await message.answer("Ktobning betlar sonini kiriting")
    await state.set_state(Form.page)


@dp.message(Form.page)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(page=message.text)
    await message.answer("Kitobning muqovasi qanaqa?")
    await state.set_state(Form.cover)


@dp.message(Form.cover)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(cover=message.text)
    await message.answer("Kitob haqidagi malumot kiring kiriting")
    await state.set_state(Form.description)


@dp.message(Form.description)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Kitob qaysi categoryga tegishli ekanligini kiriting kiriting")
    await state.set_state(Form.category)


@dp.message(Form.category)
async def state_name(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Kitobning narxini kiriting")
    await state.set_state(Form.price)


@dp.message(Form.price)
async def state_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(price=message.text)
    data = await state.get_data()
    _text = await text(data=data)
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='Ha', callback_data="Ha"),
            InlineKeyboardButton(text="Yo'q", callback_data="Yo'q"))
    await bot.send_photo(chat_id=message.chat.id, photo=data['image'], caption=_text, reply_markup=ikb.as_markup())


@dp.callback_query(F.data == 'Ha')
async def save_to_database(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='/add', callback_data="yana_add"))
    await insert(data)
    print(data)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("Saqlandi)", reply_markup=ikb.as_markup())


@dp.callback_query(F.data == "Yo'q")
async def not_save_to_database(callback: CallbackQuery, state: FSMContext, bot: Bot):
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='/add', callback_data="yana_add"))
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("Saqlanmadi)", reply_markup=ikb.as_markup())


@dp.callback_query(F.data == 'yana_add')
async def add_yana(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await state_image(callback.message, state)


@dp.callback_query(F.data.endswith("_category"))
async def category_to_book(callback: CallbackQuery, bot: Bot):
    category = callback.data.split("_category")[0]
    with engine.connect() as conn:
        res = conn.execute(Select(Book).where(Book.category == category))
        conn.commit()
    names = [i[1] for i in res]
    ikb = await inlines(names)
    await bot.edit_message_text(text=category, chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                reply_markup=ikb.as_markup())


@dp.callback_query(F.data.endswith('back'))
async def save_to_database(callback: CallbackQuery, bot: Bot):
    global _names
    ikb = await inlines(names=_names, type="category")
    res = await _select(Basket)
    count_basket = [i for i in res]
    if len(count_basket):
        ikb.row(InlineKeyboardButton(text=f"🛒 Savat ({len(count_basket)})", callback_data="savatni_och"))
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer(text="Kategoriyalardan birini tanlang", reply_markup=ikb.as_markup())


@dp.callback_query(F.data.endswith('_book'))
async def detail(callback: CallbackQuery, bot: Bot, state: FSMContext):
    global _c
    _c = 1
    book_name = callback.data.split("_book")[0]
    with engine.connect() as conn:
        res = conn.execute(Select(Book).where(Book.name == book_name))
        conn.commit()
    data = ()
    for i in res:
        await state.update_data(idsi=i[-1])
        data = i
    _text = await text(data)
    ikb = await message_inline(_c=_c)
    await bot.delete_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id)
    await bot.send_photo(chat_id=callback.message.chat.id, photo=data[0], caption=_text, reply_markup=ikb.as_markup())


@dp.message(F.text.endswith('_book'))
async def detail(message: Message, bot: Bot, state: FSMContext):
    global _c
    _c = 1
    book_name = message.text.split("_book")[0]
    with engine.connect() as conn:
        res = conn.execute(Select(Book).where(Book.name == book_name))
        conn.commit()
    data = ()
    for i in res:
        await state.update_data(idsi=i[-1])
        data = i
    _text = await text(data)
    ikb = await message_inline(_c=_c)
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.send_photo(chat_id=message.chat.id, photo=data[0], caption=_text, reply_markup=ikb.as_markup())


@dp.callback_query(F.data == 'kopayish')
async def plus(callback: CallbackQuery, bot: Bot):
    global _c
    _c += 1
    ikb = await message_inline(_c=_c)
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=ikb.as_markup())


@dp.callback_query(F.data == 'kamayish')
async def minus(callback: CallbackQuery, bot: Bot):
    global _c
    if _c == 1:
        await callback.answer("Eng kamida 1 ta kitob buyurtma qilishingiz mumkin! 😊", show_alert=True)
        return
    _c -= 1
    ikb = await message_inline(_c=_c)
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=ikb.as_markup())


@dp.callback_query(F.data == 'savatga_qoshish')
async def minus(callback: CallbackQuery, bot: Bot, state: FSMContext):
    global _names, _c
    data = await state.get_data()
    order_book_list.append({"book_id": data['idsi'], "count": _c})
    l = [int(data['idsi']), _c]
    await insert(data=l, name='a')
    res = await _select(Basket)
    count_basket = [i for i in res]
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    ikb = await inlines(names=_names, type="category")
    ikb.row(InlineKeyboardButton(text=f"🛒 Savat ({len(count_basket)})", callback_data="savatni_och"))
    await callback.message.answer(text="Kategoriyalardan birini tanlang", reply_markup=ikb.as_markup())


@dp.callback_query(F.data == 'savatni_och')
async def basket(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id)
    with engine.connect() as conn:
        query = Select(Book.name, Book.price, Basket.count).join(Book).filter(Book.id == Basket.book_id)
        res = conn.execute(query)
        conn.commit()
    l = [i for i in res]
    all = 0
    in_text = ''
    for i in range(len(l)):
        all += l[i][1] * l[i][-1]
        in_text += f"\n\n{i + 1}.{l[i][0]}\n{l[i][-1]} x {l[i][1]} = {int(l[i][1] * int(l[i][-1]))}"
    text = f"""
🛒 Savat{in_text}

Jami: {all} so'm"""
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text="❌ Savatni tozalash", callback_data="cancel"),
            InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm"),
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back"))
    ikb.adjust(1)
    await callback.message.answer(text=text, reply_markup=ikb.as_markup())


@dp.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, bot: Bot):
    with engine.connect() as conn:
        conn.execute(Delete(Basket))
        conn.commit()
    await save_to_database(callback, bot)


@dp.callback_query(F.data == "confirm")
async def cancel(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text="📞 Telefon raqam", request_contact=True))
    await callback.message.answer(text="Telefon raqamingizni qoldiring (📞 Telefon raqam tugmasini bosing)🔽:",
                                  reply_markup=rkb.as_markup())


@dp.message(F.content_type.in_({types.ContentType.CONTACT}))
async def contact(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    await state.update_data(username=message.from_user.username)
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text="❌ Yo'q", callback_data="no"),
            InlineKeyboardButton(text="✅ Ha", callback_data="yes"))
    with engine.connect() as conn:
        query = Select(Book.name, Book.price, Book.id, Basket.count).join(Book).filter(Book.id == Basket.book_id)
        res = conn.execute(query)
        conn.commit()
    l = [i for i in res]
    j = [i[2] for i in l]
    await state.update_data(book_id=j)
    all = 0
    in_text = ''
    for i in range(len(l)):
        all += l[i][1] * l[i][-1]
        in_text += f"\n\n{i + 1}.{l[i][0]}\n{l[i][-1]} x {l[i][1]} = {int(l[i][1] * int(l[i][-1]))}"
    text = f"""
🛒 Savat{in_text}

Jami: {all} so'm
Telefon raqamingiz: {message.contact.phone_number}

Buyurtma berasizmi?"""
    await message.answer(text, reply_markup=ikb.as_markup())


@dp.callback_query(F.data == 'no')
async def no(callback: CallbackQuery, bot: Bot):
    ikb = await home_buttons()
    await bot.edit_message_text("❌ Bekor qilindi", message_id=callback.message.message_id,
                                chat_id=callback.message.chat.id)
    await callback.message.answer("Asosiy menyu", reply_markup=ikb.as_markup(resize_keyboard=True))


@dp.callback_query(F.data == 'yes')
async def no(callback: CallbackQuery, bot: Bot, state: FSMContext):
    with engine.connect() as conn:
        conn.execute(Delete(Basket))
        conn.commit()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    d = await state.get_data()
    data = ["🔄 kutish holatida", d['phone_number'], d['username'], d['user_id'], order_book_list]
    naem = 'order'
    await insert(data, name=naem)
    with engine.connect() as conn:
        res = conn.execute(Select(Order).order_by(Order.id.desc()).limit(1))
        conn.commit()
    _id = 0
    for i in res:
        _id = i[-1]
    bbb = await home_buttons()
    await callback.message.answer(text=f"✅ Hurmatli mijoz! Buyurtmangiz uchun tashakkur.Buyurtma raqami: {_id}",
                                  reply_markup=bbb.as_markup(resize_keyboard=True))


@dp.message(F.text == "📞 Biz bilan bog'lanish")
async def bog(message: Message):
    await message.answer(
        "Telegram: @factorbooks_info\n\n📞 + 998950359511\n\n🤖 Bot Gafurov Fahriddin (@gafurvv) tomonidan tayyorlandi.")


@dp.message(F.text == "🔵 Biz ijtimoiy tarmoqlarda")
async def bog(message: Message):
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text="IKSR | Factor books", url='https://t.me/ikar_factor'),
            InlineKeyboardButton(text="Factor books", url="https://t.me/factor_books"),
            InlineKeyboardButton(text='"Factor book" nashriyoti', url="https://t.me/factorbooks"))
    ikb.adjust(1)
    await message.answer("Biz ijtimoiy tarmoqlarda", reply_markup=ikb.as_markup())


@dp.message(F.text == "📃 Mening buyurtmalarim")
async def order(message: Message):
    with engine.connect() as conn:
        res = conn.execute(Select(Order).where(Order.user_id == str(message.from_user.id)))
        conn.commit()
    for i in res:
        umum = 0
        title = ""
        for j in range(len(i[4])):
            with engine.connect() as conn:
                ser = conn.execute(Select(Book).where(Book.id == str(i[4][j]["book_id"])))
                conn.commit()
                k = [i for i in ser]
            umum += int(i[4][j]["count"]) * int(k[0][-2])
            title += f"""\n\n{j + 1}. 📕 Kitob nomi: {k[0][1]}\n{i[4][j]["count"]} x {k[0][-2]} = {int(i[4][j]["count"]) * int(k[0][-2])} so'm"""
        text = f"""🔢 Buyurtma raqami: {i[-1]}\n📆 Buyurtma qilingan sana: {i[-2]}\n🟣 Buyurtma holati: {i[0]}{title}\n\n 💸 Umimiy narx: {umum} so'm"""
        await message.answer(text)


@dp.inline_query()
async def inline_query_func(inline_query: InlineQuery):
    text = inline_query.query or ""
    print(text)
    res = await _select(Book)
    result = []
    book_items = [i for i in res]
    if len(text):
        l = []
        for i in book_items:
            if text.lower() in i[1].lower():
                l.append(InlineQueryResultArticle(
                    id=str(i[-1]),
                    title=i[1],
                    input_message_content=InputTextMessageContent(
                        message_text=f"{i[1]}_book"
                    ),
                    description=f"{i[-3]}\n💵 Narxi: {i[-2]}",
                    thumbnail_url=i[0]
                ))
        await inline_query.answer(l, cache_time=1)
    else:
        for i in book_items:
            result.append(InlineQueryResultArticle(
                id=str(i[-1]),
                title=i[1],
                input_message_content=InputTextMessageContent(
                    message_text=f"{i[1]}_book"
                ),
                description=f"{i[-3]}\n💵 Narxi: {i[-2]}",
                thumbnail_url=i[0]
            ))
        await inline_query.answer(result, cache_time=1)


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    commands = [BotCommand(command='start', description="Botni boshlash")]
    await bot.set_my_commands(commands)
    my_commands = [BotCommand(command='start', description='Botni boshlash'),
                   BotCommand(command='add', description="Kitob qoshish uchun")]
    for i in admins:
        await bot.set_my_commands(my_commands, BotCommandScopeChat(chat_id=i))


async def main() -> None:
    dp.startup.register(on_startup)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
