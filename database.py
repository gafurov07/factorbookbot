import datetime

from sqlalchemy import Integer, String, Text, create_engine, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, declared_attr, relationship, mapped_column, Mapped

engine = create_engine("postgresql+psycopg2://postgres:1@localhost:5432/book", echo=True)


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(self):
        result = self.__name__[0].lower()
        for i in self.__name__[1:]:
            if i.isupper():
                result += f'_{i.lower()}'
                continue
            result += i
        return result


class Book(Base):
    image: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(100))
    author: Mapped[str] = mapped_column(String(100))
    genre: Mapped[str] = mapped_column(String(100))
    translator: Mapped[str] = mapped_column(String(100))
    page: Mapped[int] = mapped_column(Integer)
    cover: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column(Integer)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    basket: Mapped["Basket"] = relationship(back_populates="book")


class Basket(Base):
    book_id: Mapped[str] = mapped_column(ForeignKey('book.id'))
    count: Mapped[int] = mapped_column(Integer)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book: Mapped["Book"] = relationship(back_populates="basket")


class Order(Base):
    order_status: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    user_id: Mapped[str] = mapped_column(String)
    book: Mapped[list] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.now(), nullable=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Category(Base):
    name: Mapped[str] = mapped_column(String(50))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
