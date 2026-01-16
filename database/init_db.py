from database import tables  # noqa: F401, E402
from database.base import Base
from database.db_env import DBEnv
from database.env_utils import get_engine


def init_db(env: DBEnv = DBEnv.EXP) -> None:
    engine = get_engine(env)
    Base.metadata.create_all(bind=engine)


def drop_db(env: DBEnv = DBEnv.EXP, allow_prod: bool = False) -> None:
    if env == DBEnv.PROD and not allow_prod:
        raise RuntimeError(
            "❌ Dropping PROD database is forbidden. "
            "Set allow_prod=True explicitly if you REALLY want to."
        )
    
    engine = get_engine(env)
    Base.metadata.drop_all(bind=engine)


def reset_db(env: DBEnv = DBEnv.EXP, allow_prod: bool = False) -> None:
    print("Dropping all tables...")
    drop_db(env, allow_prod)

    print("Recreating tables...")
    init_db(env)

    print("Database reset ✅")
