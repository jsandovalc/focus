"""Focus!

An application to help you with focusing (and resting).

Start the focused time!
Earn break time!
Rest!

Tasks

- A big button named "focus"
- Add to git repository
- Create statistics
- Gamify
- Type of works
- Different colors for break and focus!
- For every N focused minutes, X break time is earned.
- Show label in red, in case the break time is being violated.
- Add ruff and other tools.
- Add mypy.
- Store history (I can use sqlite)
- label must be bigger, and centered.
- start asyncio task only when not stopped.
- stop asyncio task if stopped.
- Add stop button.
- Another refactor.
- Create a timer class. The model, to handle changes. Split it from the window class.
- Remove the menubar.
- What can I add to ruff?
- Split other classes to other files.
- Use a font style like a digital watch.
- Center the watch.
- Implement the "breaks earned minutes."
- Sound?
- Experience.
- User statistics.
- Create an installable app.

"""

import toga
from toga.style.pack import CENTER, COLUMN, Pack
import asyncio
import datetime as dt


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

class Timer:
    """I represent a timer. Counting seconds start at zero.

    :param total_time: The total seconds I've counted while running.

    """
    def __init__(self):
        # None means "stopped"
        self._start_time: dt.datetime | None = None
        self.total_elapsed_time: int = 0

    @property
    def running(self) -> bool:
        return bool(self._start_time)

    def start(self):
        self._start_time = _now()

    def stop(self):
        self.total_elapsed_time += self.get_elapsed_seconds()
        self._start_time = None

    def get_elapsed_seconds(self) -> int:
        """I return the number of seconds since `self._start_time`"""
        if self._start_time:
            return int((_now() - self._start_time).total_seconds())

        return 0

    def get_total_elapsed_minutes_seconds(self) -> tuple[int, int]:
        return self.total_elapsed_time // 60, self.total_elapsed_time % 60

    def get_elapsed_minutes_seconds(self) -> tuple[int, int]:
        """I return a tuple of elapsed minutes and seconds.

        I'm not entirely happy with this function.

        """
        elapsed_seconds = self.get_elapsed_seconds()
        return elapsed_seconds // 60, elapsed_seconds % 60



class FocusApp(toga.App):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.start_time: dt.datetime | None = None
        self.start_break_time: dt.datetime | None = None
        self.total_focused_time: int = 0
        self.total_break_time: int = 0
        self.focused = False

        self.focused_timer = Timer()
        self.break_timer = Timer()

        self._counting_task: asynctio.Task = None

    def startup(self) -> None:
        self.main_window = toga.MainWindow()
        main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=10))

        self.timer_label = toga.Label(
            "00:00", style=Pack(padding=10, alignment=CENTER, font_size=30)
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

        self.main_window.content = main_box
        self.main_window.show()

        self._counting_task = asyncio.create_task(self._update_timers())

    def toggle_timers(self, widget) -> None:
        if self.focused_timer.running:
            self.focused_timer.stop()
            self.break_timer.start()
            minutes, seconds = self.focused_timer.get_total_elapsed_minutes_seconds()
            self.total_focused_time_label.text = f"Total focused time: {minutes:02d}:{seconds:02d}"
            self.start_button.text = "Focus!"
        else:
            self.focused_timer.start()
            self.break_timer.stop()
            minutes, seconds = self.break_timer.get_total_elapsed_minutes_seconds()
            self.total_break_time_label.text = f"Total break time: {minutes:02d}:{seconds:02d}"
            self.start_button.text = "Break!"

    async def _update_timers(self):
        """Updates the timer lables every second."""
        while True:
            if self.focused_timer.running:
                minutes, seconds = self.focused_timer.get_elapsed_minutes_seconds()
            else:
                minutes, seconds = self.break_timer.get_elapsed_minutes_seconds()

            self.timer_label.text = f"{minutes:02d}:{seconds:02d}"
            await asyncio.sleep(1)


def main():
    return FocusApp("Focus!", "org.beeware.tutorial")


if __name__ == "__main__":
    main().main_loop()
