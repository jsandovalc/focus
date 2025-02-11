from domain import Goal, Skill, Stat


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
