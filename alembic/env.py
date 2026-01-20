import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)

from config import Config
from database.base import Base
from database.db_env import DBEnv
from database.env_utils import get_engine
from database.tables import (
    AlbumORM,
    ArtistORM,
    ListeningORM,
    PlaylistORM,
    TagORM,
    TrackORM,
)
from database.tables.association_tables import (
    artist_album_association,
    artist_tag_association,
    playlist_track_association,
    similar_artist_association,
    track_artist_association,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

env = Config.APP_ENV

config_instance = Config()
databases = [
    (DBEnv.EXP, config_instance.DATABASE_URL_EXP),
    (DBEnv.TEST, config_instance.DATABASE_URL_TEST),
    (DBEnv.PROD, config_instance.DATABASE_URL_PROD),
]

for env_name, db_url in databases:

    try:
        engine = get_engine(env_name)

        if "sqlite" in db_url:
            db_path = db_url.replace("sqlite:///", "")
            if not os.path.exists(db_path):
                print(f"   📁 Création du fichier: {db_path}")

        with engine.begin() as connection:
            context.configure(connection=connection, target_metadata=Base.metadata)

            context.run_migrations()

        print(f"   ✅ {env_name} - Migration réussie")

    except Exception as e:
        print(f"   ❌ {env_name} - ERREUR: {str(e)}")
        print(f"   ⚠️  Poursuite avec les autres bases...")

print("\n" + "=" * 60)
print("MIGRATIONS TERMINÉES POUR TOUTES LES BASES")
print("=" * 60)

config.set_main_option("sqlalchemy.url", db_url)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
