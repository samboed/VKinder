import os

import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from src.db.database import User, PartnerInfo, Favorite, Blacklist, UserSetting, TempSetting, Photo, Region, City


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

    def get_temp_setting(self, vk_id):
        return self.session.query(TempSetting).filter_by(user_vk_id=vk_id).first()

    def update_temp_setting(self, vk_id, **kwargs):
        setting = self.get_temp_setting(vk_id)
        if setting:
            for key, value in kwargs.items():
                setattr(setting, key, value)
            self.session.commit()

    def get_or_create_region(self, region_id, name):
        region = self.session.query(Region).filter_by(id=region_id).first()
        if not region:
            region = Region(id=region_id, name=name)
            self.session.add(region)
            self.session.commit()
        return region

    def get_or_create_city(self, city_id, name, region_id):
        city = self.session.query(City).filter_by(id=city_id).first()
        if not city:
            city = City(id=city_id, name=name, region_id=region_id)
            self.session.add(city)
            self.session.commit()
        return city

    def add_partner(self, vk_id, first_name, last_name, bdate, city_id, region_id):
        partner = self.session.query(PartnerInfo).filter_by(vk_id=vk_id).first()
        if not partner:
            new_partner = PartnerInfo(
                vk_id=vk_id,
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

    def check_partner(self, user_vk_id, partner_vk_id):
        in_favorites = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id,
                                                              partner_vk_id=partner_vk_id).first()
        in_blacklist = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id,
                                                               partner_vk_id=partner_vk_id).first()
        return bool(in_favorites or in_blacklist)

    def get_excluded_partner_ids(self, user_vk_id):
        favorites = self.session.query(Favorite.partner_vk_id).filter_by(user_vk_id=user_vk_id).all()
        blacklist = self.session.query(Blacklist.partner_vk_id).filter_by(user_vk_id=user_vk_id).all()
        return [f.partner_vk_id for f in favorites] + [b.partner_vk_id for b in blacklist]

    def add_to_favorites(self, user_vk_id, partner_vk_id):
        exists = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if not exists:
            favorite = Favorite(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id)
            self.session.add(favorite)
            self.session.commit()
            return True
        return False

    def add_to_blacklist(self, user_vk_id, partner_vk_id):
        exists = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if not exists:
            blacklist = Blacklist(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id)
            self.session.add(blacklist)
            self.session.commit()
            return True
        return False

    def get_favorites(self, user_vk_id):
        favorites = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id).all()
        return [fav.partner for fav in favorites]

    def get_blacklist(self, user_vk_id):
        blacklist = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id).all()
        return [blocked.partner for blocked in blacklist]

    def delete_favorite(self, user_vk_id, partner_vk_id):
        fav = self.session.query(Favorite).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if fav:
            self.session.delete(fav)
            self.session.commit()
            return True
        return False

    def delete_blacklist(self, user_vk_id, partner_vk_id):
        block = self.session.query(Blacklist).filter_by(user_vk_id=user_vk_id, partner_vk_id=partner_vk_id).first()
        if block:
            self.session.delete(block)
            self.session.commit()
            return True
        return False

    def add_photo(self, vk_id, owner_id, media_id):
        exists = self.session.query(Photo).filter_by(vk_id=vk_id, owner_id=owner_id, media_id=media_id).first()
        if not exists:
            new_photo = Photo(vk_id=vk_id, owner_id=owner_id, media_id=media_id)
            self.session.add(new_photo)
            self.session.commit()


if __name__ == '__main__':
    load_dotenv()

    DSN = os.getenv('DSN')

    if not DSN:
        raise ValueError("DSN не найден")

    engine = sq.create_engine(DSN)
    db = DatabaseManager(engine)
