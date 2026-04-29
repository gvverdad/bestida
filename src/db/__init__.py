from configparser import ConfigParser
from fastapi import FastAPI

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import configure_mappers
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import TransactionChangesPlugin

from .models.sa import SQA
from .models.unique import register_nullable_unique_listeners
from ..utils.continuum import UserPlugin

sqa = SQA()
inspector = None
engine = None
make_versioned(user_cls="User", plugins=[UserPlugin(), TransactionChangesPlugin()])

# import or define all models here to ensure they are attached to the
# Model.metadata prior to any initialization routines
from .models import address
from .models import app
from .models import company
from .models import person
from .models import security
from .models import system

# use db_session for non appserver or background (server) tasks or shellserver programs
# for appserver or fastapi task use middleware db.session
db_session = scoped_session(sessionmaker())

# run configure_mappers after defining all the models to ensure
# all relationships can be setup
configure_mappers()


def get_engine(config):
    # connect_args={"check_same_thread": False}
    # ...is needed only for SQLite. not needed for other databases.
    if "sqlite" in config["sqlalchemy"]["url"]:
        return create_engine(config["sqlalchemy"]["url"], echo=False,
                             connect_args={"check_same_thread": False}
                             )
    else:
        return create_engine(config["sqlalchemy"]["url"], echo=False)


def get_session_factory(engine):
    factory = scoped_session(sessionmaker())
    factory.configure(bind=engine)
    return factory


def include_me(app: FastAPI, config: ConfigParser) -> None:
    from .models.model import Model

    global inspector
    global engine

    engine = get_engine(config)

    if not engine.dialect.has_table(engine, "Users"):
        from .scripts.initial import initialize_db

        Model.metadata.create_all(engine)
        initialize_db(engine)

    register_nullable_unique_listeners(Model)

    db_session.configure(bind=engine)
    inspector = inspect(engine)
