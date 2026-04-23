import os
import sqlalchemy as sq

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from src.db.database import (User, PartnerInfo, Favorite, Blacklist, DialogState,
                             UserSetting, TempSetting, Photo, Region, City)


class DatabaseManager:
    def __init__(self, engine):
        session = sessionmaker(bind=engine)
        self.session = session()

    def register_user(self, user_vk_id: int):
        user = self.session.query(User).filter_by(user_vk_id=user_vk_id).first()
        if not user:
            new_user = User(user_vk_id=user_vk_id)
            self.session.add(new_user)

            new_user_settings = UserSetting(user_vk_id=user_vk_id)
            self.session.add(new_user_settings)

            self.session.commit()
            return True
        return False

    def update_dialog_state(self, user_vk_id: int, state: int):
        dialog_state = self.session.query(DialogState).filter_by(user_vk_id=user_vk_id).first()
        if not dialog_state:
            dialog_state = DialogState(user_vk_id=user_vk_id)
            self.session.add(dialog_state)

        dialog_state.state = state
        self.session.commit()

    def get_dialog_state(self, user_vk_id: int):
        if not (dialog_state := self.session.query(DialogState).filter_by(user_vk_id=user_vk_id).first()):
            return -1
        return dialog_state.state


    def get_user_settings(self, user_vk_id: int):
        return self.session.query(UserSetting).filter_by(user_vk_id=user_vk_id).first()

    def update_user_setting(self, user_vk_id: int, **kwargs):
        setting = self.get_user_settings(user_vk_id)
        if setting:
            for key, value in kwargs.items():
                setattr(setting, key, value)
            self.session.commit()

    def get_temp_setting(self, user_vk_id: int):
        return self.session.query(TempSetting).filter_by(user_vk_id=user_vk_id).first()

    def update_temp_setting(self, user_vk_id: int, **kwargs):
        if not (setting := self.get_temp_setting(user_vk_id)):
            setting = TempSetting(user_vk_id=user_vk_id)
            self.session.add(setting)

        for key, value in kwargs.items():
            setattr(setting, key, value)
        self.session.commit()

    def get_region(self, region_id: int):
        return self.session.query(Region).filter_by(region_id=region_id).first()

    def add_region(self, region_id: int, name: str):
        if not self.get_region(region_id):
            region = Region(region_id=region_id, name=name)
            self.session.add(region)
            self.session.commit()

    def get_city(self, city_id: int):
        return self.session.query(City).filter_by(city_id=city_id).first()

    def add_city(self, city_id: int, name: str):
        if not self.get_city(city_id):
            city = City(city_id=city_id, name=name)
            self.session.add(city)
            self.session.commit()

    def add_partner(self, partner_vk_id: int, first_name: str, last_name: str,
                    bdate: str, city_id: int, region_id: int):
        partner = self.session.query(PartnerInfo).filter_by(partner_vk_id=partner_vk_id).first()
        if not partner:
            new_partner = PartnerInfo(
                partner_vk_id=partner_vk_id,
                first_name=first_name,
                last_name=last_name,
                bdate=bdate,
                city_id=city_id,
                region_id=region_id
            )
            self.session.add(new_partner)
            self.session.commit()
            return True
        return False

    def check_partner(self, user_vk_id: int, partner_vk_id: int):
        in_favorites = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id,
                                                              partner_vk_id=partner_vk_id).first()
        in_blacklist = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id,
                                                               partner_vk_id=partner_vk_id).first()
        return bool(in_favorites or in_blacklist)

    def get_excluded_partner_ids(self, user_vk_id: int):
        favorites = self.session.query(Favorite.partner_vk_id).filter_by(user_vk_id=user_vk_id).all()
        blacklist = self.session.query(Blacklist.partner_vk_id).filter_by(user_vk_id=user_vk_id).all()
        return [f[0] for f in favorites] + [b[0] for b in blacklist]

    def add_to_favorites(self, user_vk_id: int, partner_vk_id: int):
        exists = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if not exists:
            favorite = Favorite(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id)
            self.session.add(favorite)
            self.session.commit()
            return True
        return False

    def add_to_blacklist(self, user_vk_id: int, partner_vk_id: int):
        exists = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if not exists:
            blacklist = Blacklist(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id)
            self.session.add(blacklist)
            self.session.commit()
            return True
        return False

    def get_favorites(self, user_vk_id: int):
        favorites = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id).order_by(sq.desc(Favorite.id)).all()
        return [fav.partner for fav in favorites]

    def get_blacklist(self, user_vk_id: int):
        blacklist = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id).order_by(sq.desc(Blacklist.id)).all()
        return [blocked.partner for blocked in blacklist]

    def delete_favorite(self, user_vk_id: int, partner_vk_id: int):
        fav = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if fav:
            self.session.delete(fav)
            self.session.commit()
            return True
        return False

    def delete_blacklist(self, user_vk_id: int, partner_vk_id: int):
        block = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if block:
            self.session.delete(block)
            self.session.commit()
            return True
        return False

    def add_photo(self, partner_vk_id: int, owner_id: int, media_id: int):
        exists = self.session.query(Photo).filter_by(partner_vk_id=partner_vk_id,
                                                     owner_id=owner_id,
                                                     media_id=media_id).first()
        if not exists:
            new_photo = Photo(partner_vk_id=partner_vk_id, owner_id=owner_id, media_id=media_id)
            self.session.add(new_photo)
            self.session.commit()


if __name__ == '__main__':
    load_dotenv()

    DSN = os.getenv('DSN')

    if not DSN:
        raise ValueError("DSN не найден")

    engine = sq.create_engine(DSN)
    db = DatabaseManager(engine)
