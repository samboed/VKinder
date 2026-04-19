import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    vk_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)

    setting: Mapped["UserSetting"] = relationship(back_populates="user")


class UserSetting(Base):
    __tablename__ = 'user_settings'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.vk_id'), primary_key=True)
    state: Mapped[int] = mapped_column(sq.Integer, default=0)  # Текущий шаг меню
    age_from: Mapped[int] = mapped_column(sq.Integer, nullable=True)  # Возраст "От"
    age_to: Mapped[int] = mapped_column(sq.Integer, nullable=True)  # Возраст "До"
    sex_index: Mapped[int] = mapped_column(sq.Integer, nullable=True)  # Пол
    city_id: Mapped[int] = mapped_column(sq.Integer, nullable=True)  # ID города
    city_name: Mapped[str] = mapped_column(sq.String(100), nullable=True)  # Название города
    region_id: Mapped[int] = mapped_column(sq.Integer, nullable=True)
    region_name: Mapped[str] = mapped_column(sq.String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="setting")


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
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
