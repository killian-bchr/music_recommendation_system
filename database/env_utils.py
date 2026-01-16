from database.base import (
    SessionExp,
    SessionProd,
    SessionTest,
    engine_exp,
    engine_prod,
    engine_test,
)
from database.db_env import DBEnv
from exceptions.exceptions import UnknownEnvironment


def get_engine(env: DBEnv):
    if env == DBEnv.EXP:
        return engine_exp
    if env == DBEnv.PROD:
        return engine_prod
    if env == DBEnv.TEST:
        return engine_test

    raise UnknownEnvironment(f"Unknown environment: {env}")


def get_session_factory(env: DBEnv):
    if env == DBEnv.EXP:
        return SessionExp
    if env == DBEnv.PROD:
        return SessionProd
    if env == DBEnv.TEST:
        return SessionTest

    raise UnknownEnvironment(f"Unknown environment: {env}")
