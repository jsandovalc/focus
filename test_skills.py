import sqlite3

import pytest
from sqlalchemy.engine import Engine

from skills import SkillRepository, SkillUpdate
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool

import db


def test_store_load_skill():
    repository = SkillRepository()

    assert not repository.get_skill_by_id(1)

    new_skill = repository.create(name="Intelligence")

    assert new_skill
    assert new_skill.name == "Intelligence"

    loaded_skill = repository.get_skill_by_id(1)

    assert loaded_skill
    assert loaded_skill == new_skill  # two dataclasses are equal in this sense?


def test_update():
    repository = SkillRepository()

    new_skill = repository.create(name="Strength")

    updated_skill = repository.update(
        SkillUpdate(id=new_skill.id, xp=new_skill.xp + 10)
    )

    assert updated_skill.name == new_skill.name
    assert updated_skill.xp == (new_skill.xp + 10)
