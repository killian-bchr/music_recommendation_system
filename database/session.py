from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

from database.db_env import DBEnv
from database.env_utils import get_session_factory


@contextmanager
def get_session(env: DBEnv = DBEnv.EXP):
    session_factory = get_session_factory(env)
    session = session_factory()

    try:
        yield session

    except SQLAlchemyError:
        session.rollback()
        raise

    finally:
        session.close()
