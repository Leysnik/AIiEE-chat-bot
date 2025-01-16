import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """
    Модель пользователя в базе данных. Хранит информацию о пользователях, включая их данные, статистику и текущий прогресс
    
    Атрибуты:
        chat_id (int): Уникальный идентификатор пользователя (основной ключ)
        name (str): Имя пользователя
        forename (str): Фамилия пользователя
        group (str): Группа пользователя
        sex (str): Пол пользователя
        daily_streak (int): Количество дней подряд, когда пользователь выполнял задания
        daily_date (datetime): Дата последнего выполнения задания
        daily_total (int): Общее количество очков за выполнение заданий
        daily_complete (bool): Статус выполнения задания на текущий день
        games_total (int): Общее количество игр пользователя
    """
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
    """
    Модель истории действий пользователя. Хранит записи о действиях, выполненных пользователем, для отслеживания прогресса.
    
    Атрибуты:
        id (int): Уникальный идентификатор записи (основной ключ).
        chat_id (int): Идентификатор пользователя, которому принадлежит запись.
        name (str): Имя пользователя.
        username (str): Имя пользователя в системе.
        type (str): Тип действия.
        text (str): Описание действия.
    """
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text)
    username = db.Column(db.Text)
    type = db.Column(db.Text)
    text = db.Column(db.Text)
    
def update_daily_user_stats(session, chat_id, stats):
    """
    Обновляет ежедневную статистику пользователя в базе данных.
    
    Аргументы:
        session (Session): Сессия SQLAlchemy для выполнения операций с базой данных.
        chat_id (int): Идентификатор пользователя, чьи данные необходимо обновить.
        stats (int): Очки за выполненное задание, которые нужно добавить к общей сумме.
    """
    user = session.query(User).filter(User.chat_id == chat_id).one()
    user.daily_streak += 1
    user.daily_total += stats
    user.daily_complete = 1
    session.add(user)
    session.commit()

def make_session():
    """
    Создает и возвращает новую сессию для взаимодействия с базой данных.
    
    Возвращает:
        Session: Сессия SQLAlchemy, готовая к выполнению операций с базой данных.
    """
    engine = db.create_engine('sqlite:///AIIEE.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == '__main__':
    """
    Запускает программу и создает сессию для работы с базой данных.
    """
    session = make_session()
