import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Новый стандарт SQLAlchemy 2.0 для базового класса
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    # Используем Mapped для типизации
    vk_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)


class Candidate(Base):
    __tablename__ = 'candidates'
    vk_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(sq.String(50))
    last_name: Mapped[str] = mapped_column(sq.String(50))


class Favorite(Base):
    __tablename__ = 'favorites'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.vk_id'), primary_key=True)
    candidate_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('candidates.vk_id'), primary_key=True)

    # Связи тоже типизируем
    user: Mapped["User"] = relationship(backref='favorites')
    candidate: Mapped["Candidate"] = relationship(backref='favorited_by')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.vk_id'), primary_key=True)
    candidate_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('candidates.vk_id'), primary_key=True)

    user: Mapped["User"] = relationship(backref='blacklist')
    candidate: Mapped["Candidate"] = relationship(backref='blacklisted_by')


class Photo(Base):
    __tablename__ = 'photos'
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('candidates.vk_id'))
    url: Mapped[str] = mapped_column(sq.String(255))
    likes_count: Mapped[int] = mapped_column(sq.Integer)

    candidate: Mapped["Candidate"] = relationship(backref='photos')


def create_tables(engine):
    Base.metadata.create_all(engine)