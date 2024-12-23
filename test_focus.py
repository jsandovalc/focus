import datetime as dt
import sqlite3

import pytest

from focus import Focus


@pytest.fixture
def db() -> sqlite3.Connection:
    return sqlite3.connect("focus_test.db")


@pytest.fixture(autouse=True)
def drop_skills(db):
    with db:
        db.execute("DROP TABLE IF EXISTS skills;")


def test_get_experience_on_rest(freezer, db):
    """When ending a focus period, experience must be added."""
    app = Focus(db_name="focus_test.db")

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=25))

    app.rest()

    assert app.current_skill.xp == 10


def test_gain_a_level(db, freezer):
    """A level must be gained when achieving right amount of experience."""
    app = Focus(db_name="focus_test.db")

    app.focus()

    for _ in range(10):
        freezer.tick(delta=dt.timedelta(minutes=26))
        app.rest()
        freezer.tick(delta=dt.timedelta(seconds=10))
        app.focus()

    assert app.current_skill.xp == 0
    assert app.current_skill.level == 2
    assert app.current_skill.xp_to_next_level == 200


def test_partial_pomodoro(db, freezer):
    """Grant partial xp, if less than a pomodoro achieved."""
    app = Focus(db_name="focus_test.db")

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=10))

    app.rest()

    assert app.current_skill.xp == 4


def test_extra_pomodoro_time_capping_at_max(db, freezer):
    """Gain a little extra for longer focused times. Cap at 15 experience."""
    app = Focus(db_name="focus_test.db")

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=100))

    app.rest()

    assert app.current_skill.xp == 15
