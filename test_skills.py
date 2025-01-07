from skills import SkillRepository, SkillUpdate
from signals import level_gained, xp_gained
from domain import Skill, Stat
from repositories import SkillRepository as NewSkillRepository, StatsRepository


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


def test_event_on_increase_level():
    repository = SkillRepository()
    new_skill = repository.create(name="Strength")

    called = False

    def callback(level, xp):
        nonlocal called
        called = True

    level_gained.connect(callback)

    new_skill.gain_fixed_xp(150)

    assert called

    assert new_skill.level == 2
    assert new_skill.xp == 50
    assert new_skill.xp_to_next_level == 200

    assert repository.get_skill_by_id(new_skill.id).level == 2


def test_event_on_xp_gained():
    repository = SkillRepository()
    new_skill = repository.create(name="Strength")

    called = False
    gained_xp = 0

    def callback(skill, xp):
        nonlocal called, gained_xp
        called = True
        gained_xp = xp

    xp_gained.connect(callback)

    new_skill.gain_fixed_xp(10)

    assert called
    assert gained_xp == 10


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
