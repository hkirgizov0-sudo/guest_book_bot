from os import getenv

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship
from dotenv import load_dotenv
load_dotenv()


DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")


engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

Base = declarative_base()



class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger,primary_key=True, autoincrement=False)
    first_name: Mapped[str] = mapped_column(String(30))
    messages: Mapped[list[Messages]] = relationship(back_populates="user")


class Messages(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    note: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("users.id", ondelete="cascade"))
    user: Mapped[User] = relationship(back_populates="messages")


