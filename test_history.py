import pytest
import datetime as dt

from history import History
from timer import Lapse, LapseType
import sqlite3


def test_add_entry():
    """New entries are added to the database."""
    conn = sqlite3.connect("focus_test.db")

    with conn:
        conn.execute("DROP TABLE IF EXISTS history;")

    history = History(db_name="focus_test.db")

    now = dt.datetime.now(dt.UTC)

    lapse = Lapse(start=now, end=now + dt.timedelta(seconds=10), type=LapseType.pause)
    history.add_entries([lapse])

    entries = history.get_entries()
    assert entries
    entry = entries[0]

    print(entry.start, lapse.start)
    print(entry.end, lapse.end)
    assert entry.start == pytest.approx(lapse.start)
    assert entry.end == lapse.end
    assert entry.type == lapse.type


def test_add_repeated_entries():
    """Avoid duplication of entries."""


def test_overlapped_ranges():
    """Overlapped ranges make no sense."""


def test_calculate_yesterday_statistics():
    """Get yesterday total break time."""


def test_calculate_today_statistics():
    pass
