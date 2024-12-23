"""Focus!

An application to help you with focusing (and resting).

Start the focused time!
Earn break time!
Rest!

"""

import asyncio

import toga
from toga.style.pack import CENTER, COLUMN, ROW, Pack

from focus import Focus
from timer import duration_from_seconds


class FocusApp(toga.App):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.focus_app = Focus()

        self._counting_task: asyncio.Task | None = None

    def startup(self) -> None:
        self.main_window = toga.Window()

        timer_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=10))
        button_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding=10))

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
        timer_box.add(self.timer_label)

        self.pause_button = toga.Button(
            "Pause",
            on_press=self.toggle_pause,
            style=Pack(padding=10, alignment=CENTER),
        )

        self.start_button = toga.Button(
            "Focus!",
            on_press=self.toggle_timers,
            style=Pack(padding=10, alignment=CENTER),
        )
        self.skills_selection_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=10))
        skills: list[str] = [
            skill.name for skill in self.focus_app.skills.values()
        ]
        print(skills)
        self.skill_selection = toga.Selection(items=skills, on_change=self.change_selected_skill)
        self.skill_selection.value = skills[0]
        self.skills_selection_box.add(self.skill_selection)
        button_box.add(self.pause_button)
        button_box.add(self.start_button)
        timer_box.add(button_box)
        timer_box.add(self.skills_selection_box)

        self.total_focused_time_label = toga.Label(
            "Total focused time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        timer_box.add(self.total_focused_time_label)
        self.total_break_time_label = toga.Label(
            "Total break time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        timer_box.add(self.total_break_time_label)

        self.earned_break_time_label = toga.Label(
            "Earned break time: 0 minutes", style=Pack(padding=10, alignment=CENTER)
        )
        timer_box.add(self.earned_break_time_label)

        stats_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=10))
        today_stats = self.focus_app.history.get_statistics()
        yesterday_stats = self.focus_app.history.get_statistics()
        self.stats_focus_label = toga.Label(
            f"Today's focused time: {duration_from_seconds(today_stats.total_focus_time)}",
            style=Pack(padding=10, alignment=CENTER),
        )
        self.stats_focus_label = toga.Label(
            f"Today's focused time: {duration_from_seconds(today_stats.total_focus_time)}",
            style=Pack(padding=10, alignment=CENTER),
        )
        self.stats_rest_label = toga.Label(
            f"Today's rest time: {duration_from_seconds(today_stats.total_break_time)}",
            style=Pack(padding=10, alignment=CENTER),
        )
        self.stats_focus_yesterday_label = toga.Label(
            f"Yesterday's focused time: {duration_from_seconds(yesterday_stats.total_focus_time)}",
            style=Pack(padding=10, alignment=CENTER),
        )
        self.stats_rest_yesterday_label = toga.Label(
            f"Yesterday's rest time: {duration_from_seconds(yesterday_stats.total_break_time)}",
            style=Pack(padding=10, alignment=CENTER),
        )

        self._skills_labels = []
        for skill in self.focus_app.skills.values():
            skill_label = toga.Label(f"{skill.name}: {skill.level}")
            xp_label = toga.Label(
                f"Current xp: {skill.xp}. Next level: {skill.xp_to_next_level}"
            )
            stats_box.add(skill_label)
            stats_box.add(xp_label)
            self._skills_labels.append((skill, skill_label, xp_label))

        tabs_container = toga.OptionContainer(
            content=[("Timer", timer_box), ("Stats", stats_box)]
        )

        self.main_window.content = tabs_container
        self.main_window.show()

        self._counting_task = asyncio.create_task(self._update_timers())

    def change_selected_skill(self, widget):
        if not self.focus_app.set_current_skill(widget.value):
            widget.value = self.focus_app.current_skill.name

    def toggle_pause(self, widget) -> None:
        if self.focus_app.paused:
            self.focus_app.unpause()
        else:
            self.focus_app.pause()

    def toggle_timers(self, widget) -> None:
        if not self.focus_app.started or self.focus_app.resting:
            self.focus_app.focus()
            self.earned_break_time_label.text = (
                f"Earned break time: {self.focus_app.earned_break_time // 60} minutes"
            )
            self.start_button.text = "Break"

            if self.focus_app.earned_break_time < 0:
                self.timer_label.style.color = "red"
        else:
            self._enter_break()

    def _enter_break(self):
        self.focus_app.rest()

        self.total_focused_time_label.text = f"Total focused time: {duration_from_seconds(self.focus_app.get_total_focused_seconds())}"
        self.earned_break_time_label.text = (
            f"Earned break time: {self.focus_app.earned_break_time // 60} minutes"
        )
        self.total_break_time_label.text = f"Total break time: {duration_from_seconds(self.focus_app.get_total_rested_seconds())}"
        self.start_button.text = "Focus!"

        print(self._skills_labels)
        for skill, skill_label, xp_label in self._skills_labels:
            print("Updating label", skill, skill_label, xp_label)
            skill_label.text = f"{skill.name}: {skill.level}"
            xp_label.text = (
                f"Current xp: {skill.xp}. Next level: {skill.xp_to_next_level}"
            )

    async def _update_timers(self):
        """Updates the timer labels every second."""
        while True:
            if self.focus_app.paused:
                await asyncio.sleep(1)
                continue

            minutes, seconds = duration_from_seconds(
                self.focus_app.get_current_clock_time()
            )
            current_break_time = 0
            if self.focus_app.focusing:
                self.timer_label.style.color = "black"
                self.earned_break_time_label.text = f"Earned break time: {(self.focus_app.earned_break_time + self.focus_app.get_current_clock_time() // self.focus_app.focus_break_ratio) // 60} minutes"
                self.timer_label.text = str(
                    duration_from_seconds(self.focus_app.get_current_clock_time())
                )
                self.total_focused_time_label.text = f"Total focused time: {duration_from_seconds(self.focus_app.get_total_focused_seconds())}"
            else:
                current_break_time += self.focus_app.get_current_clock_time()

                self.earned_break_time_label.text = f"Earned break time: {(self.focus_app.earned_break_time - self.focus_app.get_current_clock_time()) // 60} minutes"
                self.timer_label.text = str(
                    duration_from_seconds(self.focus_app.get_current_clock_time())
                )
                self.total_break_time_label.text = f"Total break time: {duration_from_seconds(self.focus_app.get_total_rested_seconds())}"

            if (self.focus_app.earned_break_time - current_break_time) < 0:
                if self.focus_app.resting:
                    self.timer_label.style.color = "red"
                else:
                    self.timer_label.style.color = "black"
                self.total_break_time_label.color = "red"
            else:
                self.timer_label.style.color = "black"
                self.total_break_time_label.color = "black"

            await asyncio.sleep(1)


def main():
    return FocusApp("Focus!", "org.beeware.tutorial")


if __name__ == "__main__":
    main().main_loop()
