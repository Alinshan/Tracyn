import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from .models import Base

_engine = None
_SessionFactory = None


def init_db(config: dict = None):
    global _engine, _SessionFactory

    db_url = "sqlite:///data/tracyn.db"
    if config and "database" in config and "url" in config["database"]:
        db_url = config["database"]["url"]

    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        echo=False
    )
    Base.metadata.create_all(bind=_engine)
    _SessionFactory = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=_engine))
    return _engine


def get_db_session():
    if _SessionFactory is None:
        init_db()
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()


def get_session():
    if _SessionFactory is None:
        init_db()
    return _SessionFactory()
