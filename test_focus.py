import datetime as dt

from domain import Goal, Skill, Stat
from enums import Difficulty
from focus import Focus
from repositories import (
    GoalsRepository,
    StatsRepository,
)
from repositories import (
    SkillRepository as NewSkillRepository,
)
from signals import goal_completed


def test_stats_loaded_from_database():
    """When creating a focus instance, base stats must be loaded."""
    stats_repository = StatsRepository()
    stats_repository.create_stat(Stat(name="TestStrength"))
    stats_repository.create_stat(Stat(name="TestIntelligence"))

    app = Focus()

    assert len(app.stats) == 2


def test_load_goals_from_database():
    goals_repository = GoalsRepository()
    goals_repository.create_goal(
        Goal(
            title="Test",
            main_skill=Skill(name="test-skill", main_stat=Stat(name="main-stat")),
            secondary_skill=Skill(
                name="test-skill-2", main_stat=Stat(name="main-stat-2")
            ),
        )
    )
    goals_repository.create_goal(
        Goal(
            title="Test2",
            main_skill=Skill(name="test-skill-3", main_stat=Stat(name="main-stat-3")),
            secondary_skill=Skill(
                name="test-skill-4", main_stat=Stat(name="main-stat-4")
            ),
        )
    )

    app = Focus()

    assert len(app.goals) == 2
