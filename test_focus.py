import datetime as dt
import sqlite3

import pytest

from enums import Difficulty
from focus import Focus
from goals import Goal, GoalsRepository
from skills import SkillRepository
from repositories import SkillRepository as NewSkillRepository, StatsRepository
from domain import Skill, Stat
from signals import goal_completed
from db import get_session
from sqlmodel import delete
import models
import skills


def test_get_experience_on_rest(freezer):
    """When ending a focus period, experience must be added."""
    app = Focus()

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=25))

    app.rest()

    assert app.current_skill.xp == 10


def test_gain_a_level(freezer):
    """A level must be gained when achieving right amount of experience."""
    app = Focus()

    app.focus()

    for _ in range(10):
        freezer.tick(delta=dt.timedelta(minutes=26))
        app.rest()
        freezer.tick(delta=dt.timedelta(seconds=10))
        app.focus()

    assert app.current_skill.xp == 0
    assert app.current_skill.level == 2
    assert app.current_skill.xp_to_next_level == 200


def test_partial_pomodoro(freezer):
    """Grant partial xp, if less than a pomodoro achieved."""
    app = Focus()

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=10))

    app.rest()

    assert app.current_skill.xp == 4


def test_extra_pomodoro_time_capping_at_max(freezer):
    """Gain a little extra for longer focused times. Cap at 15 experience."""
    app = Focus()

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=100))

    app.rest()

    assert app.current_skill.xp == 15


def test_load_goals_from_db():
    """Skills must be loaded."""
    skill = SkillRepository().create_skill("test_skill")
    GoalsRepository().create_goal(
        title="test",
        description="testing",
        difficulty=Difficulty.EASY,
        skill_id=skill.id,
    )

    app = Focus()

    assert len(app.goals) == 1


def test_add_a_new_goal():
    """When a new goal is added, it get's stored and a callback is raised."""
    skill = SkillRepository().create_skill("test_skill")
    called = False

    def callback(_):
        nonlocal called
        called = True

    app = Focus()
    app.goal_added_callbacks.append(callback)
    app.add_goal(Goal(title="Test", difficulty=Difficulty.PROJECT, skill_id=skill.id))

    assert len(app.goals) == 1
    assert called


def test_complete_task():
    skill = SkillRepository().create_skill("test_skill")
    app = Focus()

    new_goal = Goal(title="Test", difficulty=Difficulty.EASY, skill_id=skill.id)
    app.add_goal(new_goal)

    called = False

    def callback(goal: Goal):
        nonlocal called

        called = True

    goal_completed.connect(callback)

    app.complete_goal(new_goal.id)

    goal = app.goals_repository.get_goal_by_id(new_goal.id)
    skill = app.skills_repository.get_skill_by_id(skill.id)

    assert goal.completed
    assert skill.xp == 5
    assert called

    called = False
    app.complete_goal(goal.id)

    assert not called


def test_complete_task_gain_level():
    """On task completion, gain a level."""
    skill = SkillRepository().create_skill("test_skill")
    app = Focus()

    goal_1 = Goal(title="Test", difficulty=Difficulty.MEDIUM, skill_id=skill.id)
    goal_2 = Goal(title="Test", difficulty=Difficulty.MEDIUM, skill_id=skill.id)
    app.add_goal(goal_1)
    app.add_goal(goal_2)

    app.complete_goal(goal_1.id)
    app.complete_goal(goal_2.id)

    skill = app.skills_repository.get_skill_by_id(skill.id)

    assert skill.xp == 0
    assert skill.level == 2


def test_complete_task_gain_several():
    """On task completion, gain a level."""
    skill = SkillRepository().create_skill("test_skill")
    app = Focus()

    goal = Goal(title="Test", difficulty=Difficulty.PROJECT, skill_id=skill.id)
    app.add_goal(goal)

    app.complete_goal(goal.id)

    skill = app.skills_repository.get_skill_by_id(skill.id)

    assert skill.xp == 200
    assert skill.level == 3


def test_skills_loaded_from_database():
    """When creating a focus instnce, skills must be loaded.

    Right now, we'll use `new_skills`, but, eventually, this will become skills.

    """
    skill_repository = NewSkillRepository()
    skill_repository.create_skill(Skill(name="TestProgramming"))
    skill_repository.create_skill(Skill(name="TestReading"))

    app = Focus()

    assert len(app.new_skills) == 2


def test_stats_loaded_from_database():
    """When creating a focus instance, base stats must be loaded."""
    stats_repository = StatsRepository()
    stats_repository.create_stat(Stat(name="TestStrength"))
    stats_repository.create_stat(Stat(name="TestIntelligence"))

    app = Focus()

    assert len(app.stats) == 2
