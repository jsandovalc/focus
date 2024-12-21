import pytest
import sqlite3
from skills import SkillRepository, SkillUpdate


@pytest.fixture
def db() -> sqlite3.Connection:
    return sqlite3.connect("focus_test.db")


def test_store_load_skill(db):
    with db:
        db.execute("DROP TABLE IF EXISTS skills;")

    repository = SkillRepository(db_path="focus_test.db")

    assert not repository.get_skill_by_id(1)

    new_skill = repository.create(name="Intelligence")

    assert new_skill
    assert new_skill.name == "Intelligence"

    loaded_skill = repository.get_skill_by_id(1)

    assert loaded_skill
    assert loaded_skill == new_skill  # two dataclasses are equal in this sense?


def test_update(db):
    with db:
        db.execute("DROP TABLE IF EXISTS skills;")

    repository = SkillRepository(db_path="focus_test.db")

    new_skill = repository.create(name="Strength")

    updated_skill = repository.update(
        SkillUpdate(id=new_skill.id, xp=new_skill.xp + 10)
    )

    assert updated_skill.name == new_skill.name
    assert updated_skill.xp == (new_skill.xp + 10)
