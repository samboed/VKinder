import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

# Импортируем классы из нашего нового расположения
from src.database import User, Candidate, Favorite, Blacklist, Photo


class DatabaseManager:
    def __init__(self, engine):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def register_user(self, vk_id):
        user = self.session.query(User).filter_by(vk_id=vk_id).first()
        if not user:
            new_user = User(vk_id=vk_id)
            self.session.add(new_user)
            self.session.commit()
            return True
        return False

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

    def check_candidate(self, user_vk_id, candidate_vk_id):
        in_favorites = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id,
                                                              candidate_vk_id=candidate_vk_id).first()
        in_blacklist = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id,
                                                               candidate_vk_id=candidate_vk_id).first()
        return bool(in_favorites or in_blacklist)


if __name__ == '__main__':
    # 1. Загружаем переменные из файла .env
    load_dotenv()

    # 2. Берем строку подключения безопасно из системы
    DSN = os.getenv('DSN')

    # Защита: если забыли создать .env
    if not DSN:
        raise ValueError("DSN не найден! Убедитесь, что создали файл .env с переменной DSN.")

    engine = sq.create_engine(DSN)
    db = DatabaseManager(engine)
    print("Подключение к БД через .env прошло успешно!")