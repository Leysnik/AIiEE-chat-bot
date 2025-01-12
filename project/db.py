import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    chat_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=False)
    name = db.Column(db.Text)
    forename = db.Column(db.Text)
    group = db.Column(db.Text)
    sex = db.Column(db.Text)
    daily_streak = db.Column(db.Integer, default=0)
    daily_date = db.Column(db.DateTime, default=datetime.now())
    daily_total = db.Column(db.Integer, default=0)
    games_total = db.Column(db.Integer, default=0)          
    
def make_session():
    engine = db.create_engine('sqlite:///AIIEE.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == '__main__':
    session = make_session()