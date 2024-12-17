import datetime as dt
import sqlite3
from dataclasses import dataclass

from timer import Lapse, LapseType

sqlite3.register_converter("DATETIME", lambda x: dt.datetime.fromisoformat(x.decode()))


@dataclass
class Stats:
    """In seconds."""

    total_focus_time: int
    total_break_time: int


class History:
    """The history is stored in db as entries with a start date and an end date.
    The start_date is unique.

    """

    def __init__(self, db_name: str = "focus.db"):
        """Initialize the sqlite db."""

        self.conn = sqlite3.connect(
            db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row

        # Primary key is to avoid inserting duplicated entries.
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
        start DATETIME PRIMARY KEY,
        end DATETIME NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('rest', 'focus', 'pause'))
        );""")

    def add_entries(self, entries: list[Lapse]):
        """Add `entries` to the history of the user."""
        with self.conn:
            for entry in entries:
                try:
                    self.conn.execute(
                        """
                    INSERT INTO history (start, end, type)
                    VALUES (?, ?, ?)
                    """,
                        (
                            entry.start,
                            entry.end,
                            entry.type,
                        ),
                    )
                except sqlite3.IntegrityError as e:
                    print("Integrity Error", e)  # noqa: T201  Later, I'll use logging.

    def get_entries(self) -> list[Lapse]:
        with self.conn:
            res = self.conn.execute(
                """
            SELECT start, end, type FROM history;
            """
            )
            return [
                Lapse(start=row["start"], end=row["end"], type=row["type"])
                for row in res.fetchall()
            ]

    def get_statistics(self, date: dt.date | None = None) -> Stats:
        """:param date: If date is None, default today will be used."""
        if date is None:
            date = dt.datetime.now(dt.UTC).date()
        if isinstance(date, dt.datetime):
            date = date.date()

        with self.conn:
            result = self.conn.execute(
                """
            SELECT IFNULL(SUM(strftime('%s', end) - strftime('%s', start)), 0) AS total_seconds
            FROM history
            WHERE date(start) = ?
            AND type = ?
            """,
                (date, LapseType.focus),
            )

            total_focus_time = result.fetchone()["total_seconds"]

        with self.conn:
            result = self.conn.execute(
                """
            SELECT IFNULL(SUM(strftime('%s', end) - strftime('%s', start)), 0) AS total_seconds
            FROM history
            WHERE date(start) = ?
            AND type = ?
            """,
                (date, LapseType.rest),
            )

            total_break_time = result.fetchone()["total_seconds"]

        return Stats(
            total_focus_time=total_focus_time, total_break_time=total_break_time
        )
