import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Region(Base):
    __tablename__ = 'regions'
    id: Mapped[int] = mapped_column(sq.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sq.String(100))


class City(Base):
    __tablename__ = 'cities'
    id: Mapped[int] = mapped_column(sq.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sq.String(100))
    region_id: Mapped[int] = mapped_column(sq.ForeignKey('regions.id'))

    region: Mapped["Region"] = relationship()


class User(Base):
    __tablename__ = 'users'
    vk_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)

    setting: Mapped["UserSetting"] = relationship(back_populates="user")
    temp_setting: Mapped["TempSetting"] = relationship(back_populates="user")


class TempSetting(Base):
    __tablename__ = 'temp_settings'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.vk_id'), primary_key=True)
    region_id: Mapped[int] = mapped_column(sq.ForeignKey('regions.id'), nullable=True)
    age_from: Mapped[int] = mapped_column(sq.Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="temp_setting")
    region: Mapped["Region"] = relationship()


class UserSetting(Base):
    __tablename__ = 'user_settings'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.vk_id'), primary_key=True)
    state: Mapped[int] = mapped_column(sq.Integer, default=0)
    age_from: Mapped[int] = mapped_column(sq.Integer, nullable=True)
    age_to: Mapped[int] = mapped_column(sq.Integer, nullable=True)
    sex_index: Mapped[int] = mapped_column(sq.Integer, nullable=True)
    city_id: Mapped[int] = mapped_column(sq.ForeignKey('cities.id'), nullable=True)

    user: Mapped["User"] = relationship(back_populates="setting")
    city: Mapped["City"] = relationship()


class PartnerInfo(Base):
    __tablename__ = 'partner_info'
    vk_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(sq.String(50))
    last_name: Mapped[str] = mapped_column(sq.String(50))
    bdate: Mapped[str] = mapped_column(sq.String(10))
    city_id: Mapped[int] = mapped_column(sq.ForeignKey('cities.id'), nullable=True)
    region_id: Mapped[int] = mapped_column(sq.ForeignKey('regions.id'), nullable=True)

    city: Mapped["City"] = relationship()
    region: Mapped["Region"] = relationship()


class Favorite(Base):
    __tablename__ = 'favorites'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.vk_id'), primary_key=True)
    partner_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('partner_info.vk_id'), primary_key=True)

    user: Mapped["User"] = relationship(backref='favorites')
    partner: Mapped["PartnerInfo"] = relationship(backref='favorited_by')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    user_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('users.vk_id'), primary_key=True)
    partner_vk_id: Mapped[int] = mapped_column(sq.ForeignKey('partner_info.vk_id'), primary_key=True)

    user: Mapped["User"] = relationship(backref='blacklist')
    partner: Mapped["PartnerInfo"] = relationship(backref='blacklisted_by')


class Photo(Base):
    __tablename__ = 'photos'
    id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)
    vk_id: Mapped[int] = mapped_column(sq.ForeignKey('partner_info.vk_id'))
    media_id: Mapped[int] = mapped_column(sq.Integer)
    owner_id: Mapped[int] = mapped_column(sq.Integer)

    partner: Mapped["PartnerInfo"] = relationship(backref='photos')


def create_tables(engine):
    Base.metadata.create_all(engine)


def drop_tables(engine):
    Base.metadata.drop_all(engine)
