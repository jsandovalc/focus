from goals import Difficulty, GoalsRepository
from skills import SkillRepository
from domain import Goal, Skill, Stat


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


def test_goal_complete():
    goal = Goal(
        title="Test",
        main_skill=Skill(name="test-skill", main_stat=Stat(name="main-stat")),
        secondary_skill=Skill(name="test-skill-2", main_stat=Stat(name="main-stat-2")),
    )

    goal.complete()

    assert goal.completed
    assert goal.main_skill.xp == 10
    assert goal.secondary_skill.xp == 5
