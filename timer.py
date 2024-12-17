import datetime as dt
from dataclasses import astuple, dataclass
from enum import StrEnum, auto


class LapseType(StrEnum):
    focus = auto()
    rest = auto()
    pause = auto()


@dataclass
class Duration:
    minutes: int
    seconds: int

    def __iter__(self):
        return iter(astuple(self))

    def __str__(self):
        return f"{self.minutes:02d}:{self.seconds:02d}"


def duration_from_seconds(seconds) -> Duration:
    """Given an amount of seconds, return a `Duration`."""
    return Duration(minutes=seconds // 60, seconds=seconds % 60)


@dataclass
class Lapse:
    start: dt.datetime
    end: dt.datetime

    type: LapseType

    def get_seconds(self) -> int:
        """The number of seconds in this lapse."""
        return int((self.end - self.start).total_seconds())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class Timer:
    """I represent a timer. Counting seconds start at zero."""

    def __init__(self) -> None:
        self._start_time: dt.datetime | None = None
        self._pause_time: dt.datetime | None = None
        self.total_elapsed_time: int = 0

        self._running_lapses: list[Lapse] = []
        self._paused_lapses: list[Lapse] = []

    @property
    def running(self) -> bool:
        return not bool(self._start_time is None) and not self.paused

    @property
    def paused(self) -> bool:
        return self._pause_time is not None

    @property
    def started(self) -> bool:
        """It's started if either, started or paused."""
        return self.running or self.paused

    @property
    def stopped(self) -> bool:
        return self._start_time is None

    def get_current_elapsed_time(self) -> int:
        """Seconds elapsed since current start time - paused_time."""
        now = _now()
        paused_time = sum(
            lapse.get_seconds()
            for lapse in self._paused_lapses
            if self._start_time and lapse.start > self._start_time
        )
        if self._pause_time:
            paused_time += int((now - self._pause_time).total_seconds())

        if not self.stopped and self._start_time:
            return int((now - self._start_time).total_seconds()) - paused_time

        return 0

    def get_current_paused_time(self) -> int:
        """Seconds this timer has been paused."""
        if self.paused and self._pause_time:
            return int((_now() - self._pause_time).total_seconds())

        return 0

    def get_total_elapsed_time(self) -> int:
        """Seconds in total this timer has been in running."""
        return self.get_current_elapsed_time() + sum(
            running_lapse.get_seconds() for running_lapse in self._running_lapses
        )

    def get_total_paused_time(self) -> int:
        """Seconds in total this timer has been in running."""
        return self.get_current_paused_time() + sum(
            paused_lapse.get_seconds() for paused_lapse in self._paused_lapses
        )

    def start(self):
        if self.running:
            return

        if not self.started:
            self._start_time = _now()

        if self.paused and self._pause_time:
            current_time = _now()
            self._paused_lapses.append(
                Lapse(start=self._pause_time, end=current_time, type=LapseType.rest)
            )
            self._pause_time = None

    def stop(self):
        if self.running or self.paused:
            self._running_lapses.append(
                Lapse(
                    start=self._start_time,
                    end=_now(),
                    type=LapseType.rest if self.paused else LapseType.focus,
                )
            )
            self.total_elapsed_time += self.get_elapsed_seconds()
            self._start_time = None
            self._pause_time = None

    def pause(self):
        if not self.started:
            return

        if self.paused:
            return

        current_time = _now()
        self._running_lapses.append(
            Lapse(start=self._start_time, end=current_time, type=LapseType.pause)
        )
        self._pause_time = current_time

    def get_elapsed_seconds(self) -> int:
        """I return the total of elapsed seconds."""
        return sum(
            running_lapse.get_seconds() for running_lapse in self._running_lapses
        ) - sum(
            paused_lapse.get_seconds()
            for paused_lapse in self._paused_lapses
            if paused_lapse.start
        )

    def get_total_elapsed_minutes_seconds(self) -> Duration:
        """I return the total of elapsed seconds for every time"""
        total_elapsed_time = self.get_elapsed_seconds()
        minutes, seconds = total_elapsed_time // 60, total_elapsed_time % 60
        return Duration(minutes=minutes, seconds=seconds)

    def get_elapsed_minutes_seconds(self) -> Duration:
        """I return a tuple of elapsed minutes and seconds since the last start."""
        now = _now()
        if self.running and self._start_time:
            elapsed_seconds = int((now - self._start_time).total_seconds())
            return Duration(minutes=elapsed_seconds // 60, seconds=elapsed_seconds % 60)

        return Duration(minutes=0, seconds=0)
