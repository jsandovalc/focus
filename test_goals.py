import sqlite3
import pytest
from goals import GoalsRepository, Difficulty
from skills import SkillRepository


def test_create_a_goal():
    skill = SkillRepository().create(name="Test")
    repository = GoalsRepository()

    goal = repository.create(
        title="Pass test",
        description="Must pass test to succeed.",
        difficulty=Difficulty.HARD,
        skill_id=skill.id,
    )

    assert goal.skill_id == skill.id
    assert goal.title == "Pass test"
    assert goal.id


def test_get_all_goals():
    skill = SkillRepository().create(name="Test")
    repository = GoalsRepository()

    repository.create_goal(
        title="Pass test",
        description="Must pass test to succeed.",
        difficulty=Difficulty.HARD,
        skill_id=skill.id,
    )
    repository.create_goal(
        title="Pass test 2",
        description="Must pass test to succeed.",
        difficulty=Difficulty.HARD,
        skill_id=skill.id,
    )

    assert len(repository.all_goals()) == 2
