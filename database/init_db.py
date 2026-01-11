from database import tables  # noqa: F401, E402
from database.base import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)


def drop_db():
    Base.metadata.drop_all(bind=engine)


def reset_db():
    print("Dropping all tables...")
    drop_db()
    print("Recreating tables...")
    init_db()
    print("Database reset ✅")
