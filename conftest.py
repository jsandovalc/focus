import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import db


@pytest.fixture(scope="session", autouse=True)
def engine():
    engine = create_engine("sqlite://", poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        return Session(engine, expire_on_commit=False)

    old_internal_session = db._get_session_internal
    db._get_session_internal = get_session_override

    yield engine

    db._get_session_internal = old_internal_session
