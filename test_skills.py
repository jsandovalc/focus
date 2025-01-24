from domain import Skill, Stat
from repositories import SkillRepository as NewSkillRepository
from repositories import StatsRepository
from signals import level_gained, xp_gained
from repositories import SkillUpdate


def test_add_xp():
    """Add xp to a skill."""
    skill = Skill(name="Test-strength", main_stat=Stat(name="test-strength"))

    skill.add_xp(xp_earned=10)

    assert skill.name == "test-strength"
    assert skill.xp == 10


def test_level_up():
    """Increase xp and gain a level."""
    skill = Skill(name="Test-strength", main_stat=Stat(name="test-strength"))

    skill.add_xp(xp_earned=150)

    assert skill.level == 2
    assert skill.xp == 50
    assert skill.xp_to_next_level == 150


def test_level_up_several_levels():
    """Gain several levels at once."""
    skill = Skill(name="Test-strength", main_stat=Stat(name="test-strength"))

    skill.add_xp(xp_earned=400)

    assert skill.level == 3
    assert skill.xp == 150
    assert skill.xp_to_next_level == 225


def test_level_up_skill_increases_related_stats():
    main_stat = Stat(name="test-strength")
    secondary_stat = Stat(name="test-int")
    skill = Skill(
        name="Test-programming", main_stat=main_stat, secondary_stat=secondary_stat
    )

    skill.add_xp(xp_earned=150)

    assert main_stat.value == 3
    assert secondary_stat.value == 2


def test_load_skill_with_stats():
    main_stat = Stat(name="test-strength")
    secondary_stat = Stat(name="test-int")

    StatsRepository().create_stat(main_stat)
    StatsRepository().create_stat(secondary_stat)
    skill = Skill(
        name="Test-programming", main_stat=main_stat, secondary_stat=secondary_stat
    )
    NewSkillRepository().create_skill(skill)
    loaded_skill = NewSkillRepository().get_skill_by_name("Test-programming")

    assert loaded_skill.main_stat.name == "test-strength"
    assert loaded_skill.secondary_stat.name == "test-int"


def test_xp_event(mocker):
    """An event is raised when increasing."""
    callback = mocker.MagicMock()
    xp_gained.connect(callback)

    main_stat = Stat(name="test-strength")
    skill = Skill(name="Test-strength", main_stat=main_stat)

    skill.add_xp(xp_earned=10)

    callback.assert_called_with(
        Skill(name="test-strength", xp=10, main_stat=main_stat), xp_earned=10
    )


def test_level_earned(mocker):
    """A signal is raised when testing level."""
    callback = mocker.MagicMock()
    level_gained.connect(callback)

    main_stat = Stat(name="test-strength")
    skill = Skill(name="Test-strength", main_stat=main_stat)

    skill.add_xp(xp_earned=150)

    callback.assert_called_with(
        Skill(
            name="test-strength",
            xp=50,
            level=2,
            main_stat=main_stat,
            xp_to_next_level=150,
        )
    )
