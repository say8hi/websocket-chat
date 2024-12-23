import datetime
from typing import Annotated
from sqlalchemy import ForeignKey, text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

# Type annotations for primary keys and timestamp columns
intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    tg_user_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    registered_at: Mapped[created_at]


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str]
    timestamp: Mapped[created_at]

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
