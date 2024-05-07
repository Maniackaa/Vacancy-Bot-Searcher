import asyncio
import datetime
from typing import Sequence

from sqlalchemy import select, delete, RowMapping

from config.bot_settings import logger
from database.db import Session, User, Search


def check_user(id):
    """Возвращает найденных пользователей по tg_id"""
    # logger.debug(f'Ищем юзера {id}')
    with Session() as session:
        user: User = session.query(User).filter(User.tg_id == str(id)).one_or_none()
        # logger.debug(f'Результат: {user}')
        return user


def get_user_from_id(pk) -> User:
    session = Session(expire_on_commit=False)
    with session:
        q = select(User).filter(User.id == pk)
        print(q)
        user = session.execute(q).scalars().one_or_none()
        return user


def get_or_create_user(user) -> User:
    """Из юзера ТГ возвращает сущестующего User ли создает его"""
    try:
        tg_id = user.id
        username = user.username
        # logger.debug(f'username {username}')
        old_user = check_user(tg_id)
        if old_user:
            # logger.debug('Пользователь есть в базе')
            return old_user
        logger.debug('Добавляем пользователя')
        with Session() as session:
            new_user = User(tg_id=tg_id,
                            username=username,
                            register_date=datetime.datetime.now()
                            )
            session.add(new_user)
            session.commit()
            logger.debug(f'Пользователь создан: {new_user}')
        return new_user
    except Exception as err:
        logger.error('Пользователь не создан', exc_info=True)


def create_search(user: User, profession, city, salary, salary_str):
    session = Session(expire_on_commit=False)
    with session:
        new_search = Search(user=user, profession=profession, city=city, salary=salary, salary_str=salary_str)
        session.add(new_search)
        session.commit()
        return new_search


def get_search(pk):
    session = Session(expire_on_commit=False)
    with session:
        q = select(Search).where(Search.id == pk)
        search = session.execute(q).scalar()
        return search


def get_active_searches() -> Sequence[Search]:
    session = Session(expire_on_commit=False)
    with session:
        q = select(Search).join(Search.user).filter(User.is_active == 1)
        search = session.execute(q).scalars().all()
        return search



async def main():
    pass
    res = get_active_searches()
    print(res)


if __name__ == '__main__':
    asyncio.run(main())

