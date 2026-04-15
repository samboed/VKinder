import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    vk_id = sq.Column(sq.BigInteger, primary_key=True)


class Candidate(Base):
    __tablename__ = 'candidates'
    vk_id = sq.Column(sq.BigInteger, primary_key=True)
    first_name = sq.Column(sq.String(50))
    last_name = sq.Column(sq.String(50))
    profile_url = sq.Column(sq.String(255))


class Favorite(Base):
    __tablename__ = 'favorites'
    user_vk_id = sq.Column(sq.BigInteger, sq.ForeignKey('users.vk_id'), primary_key=True)
    candidate_vk_id = sq.Column(sq.BigInteger, sq.ForeignKey('candidates.vk_id'), primary_key=True)

    user = relationship(User, backref='favorites')
    candidate = relationship(Candidate, backref='favorited_by')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    user_vk_id = sq.Column(sq.BigInteger, sq.ForeignKey('users.vk_id'), primary_key=True)
    candidate_vk_id = sq.Column(sq.BigInteger, sq.ForeignKey('candidates.vk_id'), primary_key=True)

    user = relationship(User, backref='blacklist')
    candidate = relationship(Candidate, backref='blacklisted_by')


class Photo(Base):
    __tablename__ = 'photos'
    id = sq.Column(sq.Integer, primary_key=True)
    # Ссылаемся на vk_id кандидата
    candidate_vk_id = sq.Column(sq.BigInteger, sq.ForeignKey('candidates.vk_id'), nullable=False)
    url = sq.Column(sq.String(255))
    likes_count = sq.Column(sq.Integer)

    # Настраиваем связь (у одного кандидата может быть несколько фото)
    candidate = relationship(Candidate, backref='photos')


def create_tables(engine):

    Base.metadata.create_all(engine)


if __name__ == '__main__':
    # логин и пароль
    DSN = 'postgresql://postgres:39912121@localhost:5432/vkinder_db'
    engine = sq.create_engine(DSN)

    create_tables(engine)
    print("БД успешно создана! Таблица Photos добавлена на место.")