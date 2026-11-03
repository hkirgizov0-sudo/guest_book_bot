import asyncio
import logging
import sys
from os import getenv

from sqlalchemy import select
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message as TelegramMessage, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session



from models import Base, engine, User, Messages

TOKEN = getenv("BOT_TOKEN")
session=Session(bind=engine)
dp = Dispatcher()


def buttons_manu():
    rkb= ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="Add Message"),
        KeyboardButton(text="My Message"),
    ])
    rkb.adjust(2)
    return rkb.as_markup(resize_keyboard=True)

class MessagesForm(StatesGroup):
    message = State()




@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    query=select(User).where(User.id==message.from_user.id)
    data=list(session.execute(query).scalars())
    btn = buttons_manu()
    if not data:
        query=insert(User).values(id=message.from_user.id, first_name=message.from_user.first_name)
        session.execute(query)
        session.commit()
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!",reply_markup=btn)



@dp.message(F.text == "Add Message")
async def add_note_handler(message: Message,state : FSMContext) -> None:
    await state.set_state(MessagesForm.message)
    await message.answer("Add Message")


@dp.message(F.text, MessagesForm.message)
async def new_note_handler(message: Message,state : FSMContext) -> None:
    message=message.text
    query=insert(Message).values(message=message , user_id=message.from_user.id)
    session.execute(query)
    session.commit()
    await state.clear()
    btn = buttons_manu()
    await message.answer("Mofaqiyatli qoshildi!",reply_markup=btn)

@dp.message(F.text == "My Message")
async def my_note_handler(message: Message, state: FSMContext) -> None:
    query = (
        select(Messages)
        .where(Messages.user_id == message.from_user.id)
        .order_by(Messages.id.desc())
        .limit(5)
    )
    messages = session.execute(query).scalars().all()

    if not messages:
        await message.answer("Sizda hali note mavjud emas!")
        return
    text = "📝 Oxirgi 5 ta note:\n\n"
    for i, note in enumerate(messages, start=1):
        text += f"{i}. {note.text}\n\n"
    await message.answer(text)





async def main() -> None:
    Base.metadata.create_all(engine)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())