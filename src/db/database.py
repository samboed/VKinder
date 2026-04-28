import sqlalchemy as sq

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.engine.base import Engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    user_vk_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)

    setting: Mapped["UserSetting"] = relationship(back_populates="user")
    temp_setting: Mapped["TempSetting"] = relationship(back_populates="user")
    dialog_state: Mapped["DialogState"] = relationship(back_populates="user")


class DialogState(Base):
    __tablename__ = 'dialog_state'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.user_vk_id'), primary_key=True)
    state: Mapped[int] = mapped_column(sq.SmallInteger, default=0)

    user: Mapped["User"] = relationship(back_populates="dialog_state")


class TempSetting(Base):
    __tablename__ = 'temp_settings'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.user_vk_id'), primary_key=True)
    region_id: Mapped[int] = mapped_column(sq.ForeignKey('regions.region_id'), nullable=True)
    age_from: Mapped[int] = mapped_column(sq.Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="temp_setting")
    region: Mapped["Region"] = relationship()


class UserSetting(Base):
    __tablename__ = 'user_settings'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.user_vk_id'), primary_key=True)
    age_from: Mapped[int] = mapped_column(sq.Integer, nullable=True)
    age_to: Mapped[int] = mapped_column(sq.Integer, nullable=True)
    sex_index: Mapped[int] = mapped_column(sq.SmallInteger, nullable=True)
    city_id: Mapped[int] = mapped_column(sq.ForeignKey('cities.city_id'), nullable=True)
    region_id: Mapped[int] = mapped_column(sq.ForeignKey('regions.region_id'), nullable=True)

    user: Mapped["User"] = relationship(back_populates="setting")
    city: Mapped["City"] = relationship()
    region: Mapped["Region"] = relationship()


class PartnerInfo(Base):
    __tablename__ = 'partner_info'
    partner_vk_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(sq.String(50))
    last_name: Mapped[str] = mapped_column(sq.String(50))
    bdate: Mapped[str] = mapped_column(sq.String(10))
    city_id: Mapped[int] = mapped_column(sq.ForeignKey('cities.city_id'), nullable=True)
    region_id: Mapped[int] = mapped_column(sq.ForeignKey('regions.region_id'), nullable=True)

    city: Mapped["City"] = relationship()
    region: Mapped["Region"] = relationship()

class Region(Base):
    __tablename__ = 'regions'
    region_id: Mapped[int] = mapped_column(sq.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sq.String(100))


class City(Base):
    __tablename__ = 'cities'
    city_id: Mapped[int] = mapped_column(sq.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sq.String(100))


class Favorite(Base):
    __tablename__ = 'favorites'
    id: Mapped[int] = mapped_column(sq.BigInteger,
                                    sq.Sequence("id_counter"),
                                    server_default=sq.FetchedValue(),
                                    autoincrement=True,
                                    nullable=False)
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.user_vk_id'), primary_key=True)
    partner_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('partner_info.partner_vk_id'), primary_key=True)

    user: Mapped["User"] = relationship(backref='favorites')
    partner: Mapped["PartnerInfo"] = relationship(backref='favorite_by')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id: Mapped[int] = mapped_column(sq.BigInteger,
                                    sq.Sequence("id_counter"),
                                    server_default=sq.FetchedValue(),
                                    autoincrement=True,
                                    nullable=False)
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.user_vk_id'), primary_key=True)
    partner_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('partner_info.partner_vk_id'), primary_key=True)

    user: Mapped["User"] = relationship(backref='blacklist')
    partner: Mapped["PartnerInfo"] = relationship(backref='blacklisted_by')


class Photo(Base):
    __tablename__ = 'photos'
    id: Mapped[int] = mapped_column(sq.Integer, primary_key=True)
    partner_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('partner_info.partner_vk_id'))
    media_id: Mapped[int] = mapped_column(sq.BigInteger)
    owner_id: Mapped[int] = mapped_column(sq.BigInteger)

    partner: Mapped["PartnerInfo"] = relationship(backref='photos')


def create_engine(dsn: str) -> Engine:
    return sq.create_engine(dsn)


def create_tables(engine: Engine):
    Base.metadata.create_all(engine)


def drop_tables(engine: Engine):
    Base.metadata.drop_all(engine)
