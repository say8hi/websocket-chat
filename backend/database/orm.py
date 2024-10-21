from operator import concat
from typing import Generic, List, Type, TypeVar
from sqlalchemy import desc, select
from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy.exc import NoResultFound
from database.database import Base

from database.models import User, Message
from schemas.messages import CachedMessageDTO

T = TypeVar("T", bound=Base)


class CRUD(Generic[T]):
    def __init__(self, model: Type[T], session_factory: sessionmaker):
        self.model = model
        self.session_factory = session_factory

    async def create(self, **kwargs) -> T:
        async with self.session_factory() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def get(self, id: int) -> T:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(id=id)
            result = await session.execute(query)
            try:
                return result.scalars().one()
            except NoResultFound:
                return None

    async def get_all(self, **kwargs) -> List[T]:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(**kwargs).order_by(desc(self.model.id))
            result = await session.execute(query)
            users = result.scalars().all()
            return users

    async def update(self, id: int, **kwargs) -> T | None:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(id=id)
            result = await session.execute(query)
            try:
                obj = result.scalars().one()
                for key, value in kwargs.items():
                    setattr(obj, key, value)

                await session.commit()
                await session.refresh(obj)
                return obj
            except NoResultFound:
                return None

    async def delete(self, id: int) -> bool:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(id=id)
            result = await session.execute(query)
            try:
                obj = result.scalars().one()
                await session.delete(obj)
                await session.commit()
                return True
            except NoResultFound:
                return False


class UsersRepo(CRUD[User]):
    def __init__(self, session):
        super().__init__(User, session)

    async def get_filter_by(self, **kwargs) -> List[User]:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)
            try:
                return result.scalars().all()
            except NoResultFound:
                return []


class MessagesRepo(CRUD[Message]):
    def __init__(self, session):
        super().__init__(Message, session)

    async def get_chat_history(
        self, sender_id: int, receiver_id: int, limit: int = 50, offset: int = 0
    ) -> List[Message]:
        async with self.session_factory() as session:
            query = (
                select(Message)
                .options(joinedload(Message.sender))
                .filter(
                    (
                        (Message.sender_id == sender_id)
                        & (Message.receiver_id == receiver_id)
                    )
                    | (
                        (Message.sender_id == receiver_id)
                        & (Message.receiver_id == sender_id)
                    )
                )
                .order_by(desc(Message.timestamp))
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(query)
            try:
                messages = result.scalars().all()
                return messages[::-1]
            except NoResultFound:
                return []

    async def add_cached_messages(self, messages: List[CachedMessageDTO]):
        async with self.session_factory() as session:
            for message in messages:
                obj = Message(
                    sender_id=message.sender_id,
                    receiver_id=message.receiver_id,
                    message=message.message,
                )
                session.add(obj)

            await session.commit()


class AsyncORM:
    session_factory: sessionmaker

    # models
    users: UsersRepo
    messages: MessagesRepo

    @classmethod
    def set_session_factory(cls, session_factory):
        cls.session_factory = session_factory

    @classmethod
    def init_models(cls):
        cls.users = UsersRepo(cls.session_factory)
        cls.messages = MessagesRepo(cls.session_factory)

    @classmethod
    async def create_tables(cls, engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
