import pytest
import datetime as dt
from focus import Focus
import sqlite3


@pytest.fixture
def db() -> sqlite3.Connection:
    return sqlite3.connect("focus_test.db")


def test_get_experience_on_rest(freezer, db):
    """When ending a focus period, experience must be added."""
    with db:
        db.execute("DROP TABLE IF EXISTS skills;")

    app = Focus(db_name="focus_test.db")

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=25))

    app.rest()

    assert app.current_skill.xp == 10


def test_gain_a_level(db, freezer):
    """A level must be gained when achieving right amount of experience."""
    with db:
        db.execute("DROP TABLE IF EXISTS skills;")

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
    with db:
        db.execute("DROP TABLE IF EXISTS skills;")

    app = Focus(db_name="focus_test.db")

    app.focus()

    freezer.tick(delta=dt.timedelta(minutes=10))

    app.rest()

    assert app.current_skill.xp == 4


def test_extra_pomodoro_time():
    pass
