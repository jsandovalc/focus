from services import SkillsService, GoalsService
from repositories import SkillRepository, GoalsRepository
from domain import Stat, Skill, Goal, Difficulty


def test_increase_level():
    """When a level is increased, the stats are increased, and that's
    stored in the database.

    """
    main_stat = Stat(name="test-strength")
    secondary_stat = Stat(name="test-int")

    skill = SkillRepository().create_skill(
        Skill(
            name="Test-programming", main_stat=main_stat, secondary_stat=secondary_stat
        )
    )
    SkillsService().grant_xp(150, skill_id=skill.id)

    updated_skill = SkillRepository().get_skill_by_id(skill.id)

    assert updated_skill.xp == 50
    assert updated_skill.level == 2
    assert updated_skill.main_stat.value == 3
    assert updated_skill.secondary_stat.value == 2


def test_complete_goal():
    """When a goal is completed, experience in some skills is
    acquired, and the stats might be updated.

    """
    main_stat = Stat(name="test-strength")
    secondary_stat = Stat(name="test-int")

    main_skill = SkillRepository().create_skill(
        Skill(
            name="Test-programming", main_stat=main_stat, secondary_stat=secondary_stat
        )
    )

    goal = Goal(
        title="Pass this test", main_skill=main_skill, difficulty=Difficulty.MEDIUM
    )

    repository = GoalsRepository()
    goal = repository.create_goal(goal)

    GoalsService().complete_goal(goal.id)

    updated_goal = repository.get_goal_by_id(goal.id)

    assert updated_goal.completed
    assert updated_goal.main_skill.level == 2
    assert updated_goal.main_skill.xp_to_next_level == 150
    assert updated_goal.main_skill.main_stat.value == 3
    assert updated_goal.main_skill.secondary_stat.value == 2
