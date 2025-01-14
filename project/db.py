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
    daily_complete = db.Column(db.Boolean, default=0)
    games_total = db.Column(db.Integer, default=0)          

class History(Base):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text)
    username = db.Column(db.Text)
    type = db.Column(db.Text)
    text = db.Column(db.Text)
    
def update_daily_user_stats(session, chat_id, stats):
    user = session.query(User).filter(User.chat_id == chat_id).one()
    user.daily_streak += 1
    user.daily_total += stats
    user.completed_daily = 1
    session.add(user)
    session.commit()
    

def make_session():
    engine = db.create_engine('sqlite:///AIIEE.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == '__main__':
    session = make_session()