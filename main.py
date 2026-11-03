import asyncio
import logging
import sys
from os import getenv

from aiogram.utils import i18n
from sqlalchemy import select
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message , KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session
from aiogram.utils.i18n import gettext as _, lazy_gettext as __, I18n, FSMI18nMiddleware

from models import Base, engine, User, Messages

TOKEN = getenv("BOT_TOKEN")
session=Session(bind=engine)
dp = Dispatcher()


def buttons_manu():
    rkb= ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text=_("Add Message")),
        KeyboardButton(text=_("My Message")),
        KeyboardButton(text=_("Language"))
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
    await message.answer(_("Hello!"),reply_markup=btn)



@dp.message(F.text == __("Add Message"))
async def add_message_handler(message: Message,state : FSMContext) -> None:
    await state.set_state(MessagesForm.message)
    await message.answer(_("Add Message"))


@dp.message(F.text, MessagesForm.message)
async def new_message_handler(message: Message,state : FSMContext) -> None:
    message_text=message.text
    query=insert(Messages).values(message=message , user_id=message.from_user.id)
    session.execute(query)
    session.commit()
    await state.clear()
    btn = buttons_manu()
    await message.answer(_("Saccesfuly Add!"),reply_markup=btn)

@dp.message(F.text == __("My Message"))
async def my_note_handler(message: Message, state: FSMContext) -> None:
    query = (
        select(Messages)
        .where(Messages.user_id == message.from_user.id)
        .order_by(Messages.id.desc())
        .limit(5)
    )
    messages = session.execute(query).scalars().all()

    if not messages:
        await message.answer(_("You don't have any messages!"))
        return
    text = _("📝 last 5 message:\n\n")
    for i, note in enumerate(messages, start=1):
        text += f"{i}. {note.text}\n\n"
    await message.answer(text)



@dp.message(F.text == __("Language"))
async def language_handler(message : Message):
    btn = [KeyboardButton(text="English"), KeyboardButton(text="Uzbek")]
    rkb=ReplyKeyboardBuilder()
    rkb.add(*btn)
    rkb.adjust(2)
    btn=rkb.as_markup(resize_keyboard=True)
    await message.answer(_("Choice language"), reply_markup=btn)

@dp.message(F.text.in_(("English", "Uzbek")))
async def choice_lang_handler(message : Message, state : FSMContext):
    map = {
        "English" : "en",
        "Uzbek" : "uz",
    }
    lang = map.get(message.text)
    await state.set_data({"locale" : lang})
    i18n.current_locale = lang
    btns = buttons_manu()
    await message.answer(_("Change Language"), reply_markup=btns)







async def main() -> None:
    i18n = I18n(path="locales", default_locale='en', domain="messages")
    dp.update.outer_middleware(FSMI18nMiddleware(i18n=i18n))
    Base.metadata.create_all(engine)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())