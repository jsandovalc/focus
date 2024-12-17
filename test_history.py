import datetime as dt
import sqlite3

import pytest

from history import History
from timer import Lapse, LapseType


@pytest.fixture
def db() -> sqlite3.Connection:
    return sqlite3.connect("focus_test.db")


def test_add_entry(db):
    """New entries are added to the database."""
    with db:
        db.execute("DROP TABLE IF EXISTS history;")

    history = History(db_name="focus_test.db")

    now = dt.datetime.now(dt.UTC)

    lapse = Lapse(start=now, end=now + dt.timedelta(seconds=10), type=LapseType.pause)
    history.add_entries([lapse])

    entries = history.get_entries()
    assert entries
    entry = entries[0]

    assert entry.start == pytest.approx(lapse.start)
    assert entry.end == lapse.end
    assert entry.type == lapse.type


def test_add_repeated_entries(db):
    """Avoid duplication of entries."""
    with db:
        db.execute("DROP TABLE IF EXISTS history;")

    now = dt.datetime.now(dt.UTC)

    history = History(db_name="focus_test.db")

    lapse = Lapse(start=now, end=now + dt.timedelta(seconds=10), type=LapseType.pause)
    history.add_entries([lapse, lapse])

    with db:
        res = db.execute("SELECT COUNT(*) FROM history")
        assert res.fetchone() == (1,)


def test_calculate_statistics(db):
    """Get yesterday total break time."""
    with db:
        db.execute("DROP TABLE IF EXISTS history;")

    history = History(db_name="focus_test.db")

    stats = history.get_statistics()

    assert stats.total_focus_time == 0
    assert stats.total_break_time == 0

    now = dt.datetime.now(dt.UTC)

    focus_lapse = Lapse(
        start=now, end=now + dt.timedelta(seconds=10), type=LapseType.focus
    )
    break_lapse = Lapse(
        start=now + dt.timedelta(seconds=10),
        end=now + dt.timedelta(seconds=25),
        type=LapseType.rest,
    )
    history.add_entries([focus_lapse, break_lapse])

    stats = history.get_statistics()

    assert stats.total_focus_time == 10
    assert stats.total_break_time == 15

    one_day = dt.timedelta(days=1)
    yesterday = dt.datetime.now(dt.UTC) - one_day
    focus_lapse = Lapse(
        start=now - one_day,
        end=now - one_day + dt.timedelta(seconds=30),
        type=LapseType.focus,
    )
    break_lapse = Lapse(
        start=now - one_day + dt.timedelta(seconds=20),
        end=now - one_day + dt.timedelta(seconds=70),
        type=LapseType.rest,
    )
    history.add_entries([focus_lapse, break_lapse])

    stats = history.get_statistics(date=yesterday)

    assert stats.total_focus_time == 30
    assert stats.total_break_time == 50
