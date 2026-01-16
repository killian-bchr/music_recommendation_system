from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import Config

engine_prod = create_engine(Config.DATABASE_URL_PROD, echo=False)
engine_exp = create_engine(Config.DATABASE_URL_EXP, echo=False)

SessionProd = sessionmaker(bind=engine_prod, autoflush=False, autocommit=False)
SessionExp = sessionmaker(bind=engine_exp, autoflush=False, autocommit=False)

Base = declarative_base()
