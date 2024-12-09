"""Focus!

An application to help you with focusing (and resting).

Start the focused time!
Earn break time!
Rest!

Tasks

- Implement pause.
  - Add a pause button.
  - What to do when paused?
- Refactor again.
- Create statistics
- Gamify
- Type of works
- Add ruff and other tools.
- Add mypy.
- Ruff plugins
- Store history (I can use sqlite)
- Add stop button.
- Another refactor.
- What can I add to ruff?
- Split other classes to other files.
- Sound? Tic tac might work.
- Experience.
- Skills (my idea of gamification).
- User statistics.
- Create an installable app.
- Notifications?
- Increase size of button.
- Add tests.
- Labels for "type of work".
- Use sqlite to store between sessions.
- Use a src directory structure.
- tox?
- Set goals? (sometimes, must switch between goals.)
- Add ticker sound?
- Upload to github.
- Add experience (some way of grinding)
- Parametrize labels.
- How can I count/handle interruptions? Can read, can think.
- Add keyboard shortcuts.
- Use red if balance is negative.
- Make the ratio configurable.
- Prizes for everyday usage. Habits ??
- Restart the label to 00:00 when switching. (a minor visual improvement)
- Implement a pause, or is the same as interruption?
- Handle interruptions? What is an interruption? How can the be handled? Counted?
- Add a README.
- Show watch in notifications.
- Show in red if balance negative (earned_time_label).
- Store session: how?
- Define principles (for example, sensible defaults, and, also, )

"""

import toga
from toga.style.pack import CENTER, COLUMN, Pack
import asyncio
import datetime as dt
from dataclasses import dataclass, astuple


@dataclass
class Duration:
    minutes: int
    seconds: int

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class Lapse:
    start: dt.datetime
    end: dt.datetime

    def get_seconds(self) -> int:
        """The number of seconds in this lapse."""
        return int((self.end - self.start).total_seconds())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Timer:
    """I represent a timer. Counting seconds start at zero.

    :ivar total_time: The total seconds I've counted while running.

    """

    def __init__(self):
        # None means "stopped"
        self._start_time: dt.datetime | None = None
        self._pause_time: dt.datetime | None = None
        self.total_elapsed_time: int = 0

        self._running_lapses = []
        self._paused_lapses = []

    @property
    def running(self) -> bool:
        return bool(self._start_time)

    def start(self):
        self._start_time = _now()

    def stop(self):
        if self.running:
            self._running_lapses.append(Lapse(start=self._start_time, end=_now()))
            self.total_elapsed_time += self.get_elapsed_seconds()
            self._start_time = None

    def pause(self):
        current_time = _now()
        if self.running:
            self._running_lapses.append(Lapse(start=self._start_time, end=current_time))
            self._start_time = None
            self._paused_time = current_time
        else:
            self._paused_lapses.append(Lapse(start=self._paused_time, end=current_time))
            self._start_time = current_time

    def get_elapsed_seconds(self) -> int:
        """I return the number of seconds since `self._start_time`"""
        return sum(
            running_lapse.get_seconds() for running_lapse in self._running_lapses
        ) - sum(paused_lapse.get_seconds() for paused_lapse in self._paused_lapses)

    def get_total_elapsed_minutes_seconds(self) -> Duration:
        """I return the total of elapsed seconds for every time"""
        minutes, seconds = self.total_elapsed_time // 60, self.total_elapsed_time % 60
        return Duration(minutes=minutes, seconds=seconds)

    def get_elapsed_minutes_seconds(self) -> Duration:
        """I return a tuple of elapsed minutes and seconds since the last start."""
        elapsed_seconds = self.get_elapsed_seconds()
        return Duration(elapsed_seconds // 60, elapsed_seconds % 60)


class FocusApp(toga.App):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.focused_timer = Timer()
        self.break_timer = Timer()

        self._counting_task: asynctio.Task = None
        self._total_earned_time: int = 0  # in seconds. Shown in minutes.
        self._focused_break_ratio = 3

    def startup(self) -> None:
        self.main_window = toga.Window()
        main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=10))

        self.timer_label = toga.Label(
            "00:00",
            style=Pack(
                padding=10,
                alignment=CENTER,
                font_size=150,
                display="pack",
                direction="column",
                text_align=CENTER,
            ),
        )
        main_box.add(self.timer_label)

        self.start_button = toga.Button(
            "Focus!",
            on_press=self.toggle_timers,
            style=Pack(padding=10, alignment=CENTER),
        )
        main_box.add(self.start_button)

        self.total_focused_time_label = toga.Label(
            "Total focused time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        main_box.add(self.total_focused_time_label)
        self.total_break_time_label = toga.Label(
            "Total break time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        main_box.add(self.total_break_time_label)

        self.earned_break_time_label = toga.Label(
            "Earned break time: 0 minutes", style=Pack(padding=10, alignment=CENTER)
        )
        main_box.add(self.earned_break_time_label)

        self.main_window.content = main_box
        self.main_window.show()

        self._counting_task = asyncio.create_task(self._update_timers())

    def toggle_timers(self, widget) -> None:
        if self.focused_timer.running:
            self._total_earned_time += (
                self.focused_timer.get_elapsed_seconds() // self._focused_break_ratio
            )
            self.earned_break_time_label.text = (
                f"Earned break time: {self._total_earned_time // 60} minutes"
            )
            self.focused_timer.stop()
            self.break_timer.start()
            minutes, seconds = self.focused_timer.get_total_elapsed_minutes_seconds()
            self.total_focused_time_label.text = (
                f"Total focused time: {minutes:02d}:{seconds:02d}"
            )
            self.start_button.text = "Focus!"

            if self._total_earned_time < 0:
                self.timer_label.style.color = "red"
        else:
            self._total_earned_time -= self.break_timer.get_elapsed_seconds()
            self.earned_break_time_label.text = (
                f"Earned break time: {self._total_earned_time // 60} minutes"
            )
            self.break_timer.stop()
            self.focused_timer.start()
            minutes, seconds = self.break_timer.get_total_elapsed_minutes_seconds()
            self.total_break_time_label.text = (
                f"Total break time: {minutes:02d}:{seconds:02d}"
            )
            self.start_button.text = "Break!"

    async def _update_timers(self):
        """Updates the timer labels every second."""
        while True:
            if self.focused_timer.running:
                self.timer_label.style.color = "black"
                minutes, seconds = self.focused_timer.get_elapsed_minutes_seconds()
                self.earned_break_time_label.text = f"Earned break time: {(self._total_earned_time + self.focused_timer.get_elapsed_seconds() // self._focused_break_ratio) // 60} minutes"
            else:
                minutes, seconds = self.break_timer.get_elapsed_minutes_seconds()
                self.earned_break_time_label.text = f"Earned break time: {(self._total_earned_time - self.break_timer.get_elapsed_seconds()) // 60} minutes"

                if self._total_earned_time < 0:
                    self.timer_label.style.color = "red"

            self.timer_label.text = f"{minutes:02d}:{seconds:02d}"

            await asyncio.sleep(1)


def main():
    return FocusApp("Focus!", "org.beeware.tutorial")


if __name__ == "__main__":
    main().main_loop()
