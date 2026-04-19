import os

import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from src.database import User, Candidate, Favorite, Blacklist, UserSetting, Photo


class DatabaseManager:
    def __init__(self, engine):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def register_user(self, vk_id):
        user = self.session.query(User).filter_by(vk_id=vk_id).first()
        if not user:
            new_user = User(vk_id=vk_id)
            self.session.add(new_user)

            new_settings = UserSetting(user_vk_id=vk_id)
            self.session.add(new_settings)

            self.session.commit()
            return True
        return False

    def get_user_settings(self, vk_id):
        return self.session.query(UserSetting).filter_by(user_vk_id=vk_id).first()

    def update_user_setting(self, vk_id, **kwargs):
        setting = self.get_user_settings(vk_id)
        if setting:
            for key, value in kwargs.items():
                setattr(setting, key, value)
            self.session.commit()

    def add_candidate(self, vk_id, first_name, last_name):
        candidate = self.session.query(Candidate).filter_by(vk_id=vk_id).first()
        if not candidate:
            new_candidate = Candidate(vk_id=vk_id, first_name=first_name, last_name=last_name)
            self.session.add(new_candidate)
            self.session.commit()
            return True
        return False

    def update_candidate(self, vk_id, new_first_name, new_last_name):
        candidate = self.session.query(Candidate).filter_by(vk_id=vk_id).first()
        if candidate:
            candidate.first_name = new_first_name
            candidate.last_name = new_last_name
            self.session.commit()

    def check_candidate(self, user_vk_id, candidate_vk_id):
        in_favorites = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id,
                                                              candidate_vk_id=candidate_vk_id).first()
        in_blacklist = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id,
                                                               candidate_vk_id=candidate_vk_id).first()
        return bool(in_favorites or in_blacklist)

    def add_to_favorites(self, user_vk_id, candidate_vk_id):
        exists = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id).first()
        if not exists:
            favorite = Favorite(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id)
            self.session.add(favorite)
            self.session.commit()
            return True
        return False

    def add_to_blacklist(self, user_vk_id, candidate_vk_id):
        exists = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id).first()
        if not exists:
            blacklist = Blacklist(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id)
            self.session.add(blacklist)
            self.session.commit()
            return True
        return False

    def get_favorites(self, user_vk_id):
        favorites = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id).all()
        return [fav.candidate for fav in favorites]

    def get_blacklist(self, user_vk_id):
        blacklist = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id).all()
        return [blocked.candidate for blocked in blacklist]

    def delete_favorite(self, user_vk_id, candidate_vk_id):
        fav = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id).first()
        if fav:
            self.session.delete(fav)
            self.session.commit()
            return True
        return False

    def delete_blacklist(self, user_vk_id, candidate_vk_id):
        block = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id).first()
        if block:
            self.session.delete(block)
            self.session.commit()
            return True
        return False

    def add_photo(self, candidate_vk_id, url, likes_count):
        new_photo = Photo(candidate_vk_id=candidate_vk_id, url=url, likes_count=likes_count)
        self.session.add(new_photo)
        self.session.commit()


if __name__ == '__main__':
    load_dotenv()

    DSN = os.getenv('DSN')

    if not DSN:
        raise ValueError("DSN не найден! Убедитесь, что создали файл .env с переменной DSN.")

    engine = sq.create_engine(DSN)
    db = DatabaseManager(engine)
    print("Подключение к БД через .env прошло успешно!")
