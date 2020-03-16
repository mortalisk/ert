import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ert_shared.storage import Base


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:", echo=True)


@pytest.yield_fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.yield_fixture
def db_session(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
