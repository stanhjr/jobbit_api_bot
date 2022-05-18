import time
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import Table, Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

from deploy.deploy_config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)


@contextmanager
def session():
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    try:
        yield db_session
    except Exception as e:
        print(e)
    finally:
        db_session.remove()
        connection.close()


association_table = Table('association', Base.metadata,
                          Column('jobbit_users_id', ForeignKey('jobbit_users.id'), primary_key=True),
                          Column('skills_id', ForeignKey('skills.id'), primary_key=True)
                          )


class Users(Base):
    __tablename__ = 'jobbit_users'
    id = Column(BigInteger, unique=True, primary_key=True)
    telegram_id = Column(BigInteger)
    username = Column(String(120))
    first_name = Column(String(120))
    last_name = Column(String(120))
    registration_date = Column(BigInteger)
    telegram_language = Column(String(20))
    website_language = Column(String(20))
    is_banned = Column(Integer, default=0)

    is_active = Column(Integer, default=1)
    notification_counter = Column(Integer, default=0)

    first_message = Column(Integer, default=0)
    website_id = Column(BigInteger)
    website_name = Column(String(120))
    website_role = Column(Integer, default=1)
    messages_allowed = Column(Integer, default=1)
    other_alerts_allowed = Column(Integer, default=1)
    skills = relationship("Skills", secondary=association_table, back_populates="users")

    def __init__(self, telegram_id, username, first_name, last_name, telegram_language, website_language, website_name, website_role, website_id):
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.website_id = website_id
        self.website_role = website_role
        self.telegram_language = telegram_language
        self.website_language = website_language
        self.website_name = website_name
        self.registration_date = round(time.time())

    @property
    def get_date_add(self):
        return datetime.fromtimestamp(self.date_add).strftime('%Y-%m-%d')


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(BigInteger, unique=True, primary_key=True)
    skill_id = Column(BigInteger, unique=True)
    skill_name = Column(String(120), nullable=False, unique=True)
    users = relationship("Users", secondary=association_table, back_populates="skills")

    def __init__(self, skill_name, skill_id):
        self.skill_name = skill_name
        self.skill_id = skill_id

    def get_dict(self):
        return {"skill_id": self.skill_id, "skill_name": self.skill_name}


Base.metadata.create_all(engine)
