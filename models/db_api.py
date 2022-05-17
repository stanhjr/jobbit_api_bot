import smtplib

from sqlalchemy.orm import contains_eager
from sqlalchemy.sql import func, functions
from sqlalchemy.sql.elements import and_

from models.tabs import session, Users, Skills, association_table
from aiogram import types


def is_number(string):
    try:
        string = string.replace(" ", "")
        string = string.replace(",", ".")
        return float(string)
    except ValueError:
        return False


class DataApi:
    def __init__(self):
        self.session = session

    def get_user(self, message: types.Message):
        with self.session() as s:
            return s.query(Users).filter(Users.telegram_id == message.from_user.id).first()

    def get_user_website_id(self, message: types.Message):
        with self.session() as s:
            users = s.query(Users.website_id).filter(Users.telegram_id == message.from_user.id).first()
            if users:
                return users[0]

    def enable_message_allowed(self, message: types.Message):
        with self.session() as s:
            s.query(Users).filter(Users.telegram_id == message.from_user.id).update({'messages_allowed': 1})
            s.commit()

    def disable_message_allowed(self, message: types.Message):
        with self.session() as s:
            s.query(Users).filter(Users.telegram_id == message.from_user.id).update({'messages_allowed': .0})
            s.commit()

    def enable_other_alerts_allowed(self, message: types.Message):
        with self.session() as s:
            s.query(Users).filter(Users.telegram_id == message.from_user.id).update({'other_alerts_allowed': 1})
            s.commit()

    def disable_other_alerts_allowed(self, message: types.Message):
        with self.session() as s:
            s.query(Users).filter(Users.telegram_id == message.from_user.id).update({'other_alerts_allowed': 0})
            s.commit()

    def create_user(self, message: types.Message, data: dict):
        with self.session() as s:
            user = Users(telegram_id=message.from_user.id,
                         username=message.from_user.username,
                         first_name=message.from_user.first_name,
                         last_name=message.from_user.last_name,
                         telegram_language=message.from_user.language_code,
                         website_id=data['data']['id'],
                         website_name=data['data']['name'],
                         website_role=data['data']['role'],
                         website_language=data['data']['lang'],
                         )
            s.add(user)
            s.commit()

    # def delete_user(self, message: types.Message):
    #     with self.session() as s:
    #         s.query(Users).filter(telegram_id=message.from_user.id).delete()
    #         s.commit()

    def delete_user(self, message: types.Message):
        with self.session() as s:
            s.query(Users).filter(telegram_id=message.from_user.id).update({'is_active': 0})
            s.commit()

    def add_skills(self, message: types.Message, skill_list: list):
        with self.session() as s:
            user = s.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            all_skills = s.query(Skills).filter(Skills.skill_name.in_(skill_list)).all()
            all_skills_name_model = [x.skill_name for x in all_skills]
            new_skill_list = list(filter(lambda x: x not in all_skills_name_model, skill_list))

            for model in all_skills:
                user.skills.append(model)

            for skill in new_skill_list:
                skill = Skills(skill_name=skill)
                user.skills.append(skill)
                s.add(user)
            s.commit()

    def add_skill_for_user(self, message: types.Message, skill_id, skill_name):
        with self.session() as s:
            user = s.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            skill = s.query(Skills).filter(Skills.skill_id == skill_id).first()
            if not skill:
                skill = Skills(skill_id=skill_id, skill_name=skill_name)
            user.skills.append(skill)
            s.add(user)
            s.commit()

    def delete_skill_for_user(self, message: types.Message, skill_id):
        with self.session() as s:
            user = s.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            skill = s.query(Skills).filter(Skills.skill_id == skill_id).first()
            s.query(association_table).filter(and_(association_table.c.skills_id == skill.id),
                                              association_table.c.jobbit_users_id == user.id).delete()

            s.commit()

    def delete_all_skill_for_user(self, message: types.Message):
        with self.session() as s:
            user = s.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            s.query(association_table).filter(association_table.c.jobbit_users_id == user.id).delete()
            s.commit()

    def check_skill_for_user(self, message: types.Message, skill_id):
        with self.session() as s:
            user = s.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            skill = s.query(Skills).filter(Skills.skill_id == skill_id).first()
            association = s.query(association_table).filter(and_(association_table.c.skills_id == skill.id),
                                                            association_table.c.jobbit_users_id == user.id).first()

            if association:
                return True
            return False

    def get_user_skills(self, message: types.Message):
        with self.session() as s:
            user = s.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            skills = s.query(Skills).filter(association_table.c.jobbit_users_id == user.id,
                                            association_table.c.skills_id == Skills.id).all()

            return [skill.get_dict() for skill in skills], [skill.skill_id for skill in skills]

    def get_user_list_skill_id(self, message: types.Message):
        with self.session() as s:
            user = s.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            skills = s.query(Skills).filter(association_table.c.jobbit_users_id == user.id,
                                            association_table.c.skills_id == Skills.id).all()

            if user.website_role == 1:
                my_side = 'vacancy'
            else:
                my_side = 'candidate'

            return [skill.skill_id for skill in skills], my_side, user.website_id

    def get_user_settings(self, message: types.Message):
        with self.session() as s:
            settings = s.query(Users.other_alerts_allowed,
                               Users.messages_allowed).filter(Users.telegram_id == message.from_user.id).first()
            return {"other_alerts_allowed": settings[0], "messages_allowed": settings[1]}

    def get_candidate_telegram_id(self, website_id):
        with self.session() as s:
            users = s.query(Users.telegram_id).filter(and_(Users.website_id == website_id,
                                                           Users.other_alerts_allowed == 1,
                                                           Users.website_role == 1,
                                                           Users.is_active == 1)).all()
            if users:
                return list(set([user[0] for user in users]))

    def get_employer_telegram_id(self, website_id):
        with self.session() as s:
            users = s.query(Users.telegram_id).filter(and_(Users.website_id == website_id,
                                                           Users.other_alerts_allowed == 1,
                                                           Users.website_role == 2,
                                                           Users.is_active == 1)).all()
            if users:
                return list(set([user[0] for user in users]))

    def get_user_telegram_id(self, website_id):
        with self.session() as s:
            users = s.query(Users.telegram_id).filter(and_(Users.website_id == website_id,
                                                           Users.other_alerts_allowed == 1,
                                                           Users.is_active == 1)).all()

            if users:
                return list(set([user[0] for user in users]))

    def user_notification_counter_update(self, website_id):
        with self.session() as s:
            user = s.query(Users).filter(and_(Users.is_active == 1,
                                              Users.website_id == website_id)).first()
            user.notification_counter += 1
            s.add(user)
            # s.query(Users).filter(and_(Users.is_active == 1,
            #                            Users.website_id == website_id)
            #                       ).update({"notification_counter": Users.notification_counter + 1})
            s.commit()

    def get_count_of_active_user(self):
        with self.session() as s:
            return s.query(Users.id).filter(Users.is_active == 1).count()

    def get_sum_notifications(self):
        with self.session() as s:
            return s.query(func.sum(Users.notification_counter)).scalar()

    # def copy_user(self):
    #     with self.session() as s:
    #         user = s.query(Users).first()
    #         new_user = Users(telegram_id=user.telegram_id,
    #                          username=user.username,
    #                          first_name=user.first_name,
    #                          last_name=user.last_name,
    #                          telegram_language=user.telegram_language,
    #                          website_id=user.website_id,
    #                          website_name=user.website_name,
    #                          website_role=user.website_role,
    #                          website_language=user.website_language,
    #                          )
    #         new_user.notification_counter = 2
    #         s.add(new_user)
    #         s.commit()


data_api = DataApi()
