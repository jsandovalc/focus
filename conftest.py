import pytest
from sqlmodel import Session, SQLModel, create_engine, delete
from sqlmodel.pool import StaticPool
from db import get_session
import models

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


@pytest.fixture(autouse=True)
def delete_skills(engine):
    with get_session() as session:
        session.exec(delete(models.GoalModel))
        session.exec(delete(models.SkillModel))
        session.exec(delete(models.StatModel))
        session.commit()
