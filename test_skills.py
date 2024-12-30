from skills import SkillRepository, SkillUpdate
from signals import level_gained, xp_gained


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
