import os
import sys
# ruff: noqa: E402

# Ensure project root is on sys.path so tests can import `backend` package
ROOT = os.getcwd()
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import main as app_mod
from backend.app.db import models
from backend.app.db.session import get_db


@pytest.fixture(scope="session")
def engine_and_tables():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(engine_and_tables):
    Session = sessionmaker(bind=engine_and_tables)
    session = Session()
    try:
        yield session
    finally:
        session.close()


# Provide a dependency override that yields the in-memory DB session
def _override_get_db(db_session):
    def _gen():
        try:
            yield db_session
        finally:
            pass
    return _gen


@pytest.fixture()
def client(db_session):
    # Override the dependency
    app = app_mod.app
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
