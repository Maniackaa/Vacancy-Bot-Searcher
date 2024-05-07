import dataclasses
import datetime

from sqlalchemy import create_engine, ForeignKey, String, DateTime, \
    Integer, select, delete, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database


# db_url = f"postgresql+psycopg2://{conf.db.db_user}:{conf.db.db_password}@{conf.db.db_host}:{conf.db.db_port}/{conf.db.database}"
from config.bot_settings import BASE_DIR, logger

db_path = BASE_DIR / 'base.sqlite'
db_url = f"sqlite:///{db_path}"
engine = create_engine(db_url, echo=False)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    def set(self, key, value):
        _session = Session(expire_on_commit=False)
        with _session:
            if isinstance(value, str):
                value = value[:999]
            setattr(self, key, value)
            _session.add(self)
            _session.commit()
            logger.debug(f'Изменено значение {key} на {value}')
            return self

    def del_obj(self):
        try:
            _session = Session(expire_on_commit=False)
            with _session:
                q = delete(self.__class__).where(self.__class__.id==self.id)
                _session.execute(q)
                _session.commit()
        except Exception as err:
            logger.error(err)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    tg_id: Mapped[str] = mapped_column(String(30), unique=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    register_date: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=True)
    fio: Mapped[str] = mapped_column(String(200), nullable=True)
    is_active: Mapped[int] = mapped_column(Integer(), default=0)
    phone: Mapped[str] = mapped_column(String(100), nullable=True)
    age: Mapped[int] = mapped_column(Integer(), nullable=True)
    write_to: Mapped[str] = mapped_column(String(20), nullable=True)
    balance: Mapped[float] = mapped_column(Integer(), default=0)
    searches: Mapped[list['Search']] = relationship(back_populates='user',  lazy='selectin')

    def __repr__(self):
        return f'{self.id}. {self.username or "-"} {self.tg_id}'


class Search(Base):
    __tablename__ = 'searches'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped[User] = relationship(back_populates="searches", lazy='selectin')
    created: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=True,
                                                       default=lambda: datetime.datetime.now())
    profession: Mapped[str] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    salary_str: Mapped[str] = mapped_column(String(100), nullable=True)
    salary: Mapped[int] = mapped_column(Integer(), nullable=True)

    def __str__(self):
        return f'{self.profession}, {self.city}, {self.salary_str}'


@dataclasses.dataclass
class ProfResult:
    id: str
    title: str
    city: str
    link: str
    salary: str

    def __str__(self):
        return f'{self.title}, {self.salary}, {self.city}, {self.link}'


if not database_exists(db_url):
    create_database(db_url)
Base.metadata.create_all(engine)
