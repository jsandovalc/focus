"""Focus!

An application to help you with focusing (and resting).

Start the focused time!
Earn break time!
Rest!

"""

import asyncio
from dataclasses import dataclass

import toga
from toga.style.pack import CENTER, COLUMN, ROW, Pack, LEFT

from focus import Focus
from timer import duration_from_seconds
from models import Goal
from enums import Difficulty
from functools import partialmethod
from signals import level_gained, xp_gained


class NewGoalDialog(toga.Window):
    def __init__(self, title: str, focus_app: Focus):
        super().__init__(title=title, resizable=False, size=(400, 300))

        common_style = Pack(padding=10)
        self.textinput = toga.TextInput()
        self.ok_button = toga.Button(
            "Save", on_press=self.on_accept, style=common_style
        )
        self.cancel_button = toga.Button(
            "Cancel", on_press=self.on_cancel, style=common_style
        )
        self.content = toga.Box(style=Pack(direction=COLUMN, padding=10))

        title_label = toga.Label("Goal title:", style=common_style)
        self.title_input = toga.TextInput(style=common_style)
        description_label = toga.Label("Goal description:", style=common_style)
        self.description_input = toga.MultilineTextInput()
        difficulty_label = toga.Label(" Difficulty:", style=common_style)
        self.difficulty_selection = toga.Selection(
            items=[enum.value for enum in Difficulty], style=common_style
        )
        skill_label = toga.Label("Skill:", style=Pack(padding=(0, 5)))
        self.skill_selection = toga.Selection(
            items=[skill.name for skill in focus_app.skills.values()],
            style=common_style,
        )

        self.content.add(title_label)
        self.content.add(self.title_input)
        self.content.add(description_label)
        self.content.add(self.description_input)
        self.content.add(difficulty_label)
        self.content.add(self.difficulty_selection)
        self.content.add(skill_label)
        self.content.add(self.skill_selection)
        self.content.add(self.ok_button)
        self.content.add(self.cancel_button)

        self.future = self.app.loop.create_future()

    def on_accept(self, widget, **kwargs):
        self.future.set_result("Save")
        self.close()

    def on_cancel(self, widget, **kwargs):
        self.future.set_result("Cancel")
        self.close()

    def __await__(self):
        return self.future.__await__()


class FocusApp(toga.App):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.focus_app = Focus()
        self._counting_task: asyncio.Task | None = None
        self.focus_app.goal_added_callbacks.append(self.goal_added)

        level_gained.connect(self.level_gained)
        xp_gained.connect(self.xp_gained)

    def level_gained(self, skill, xp):
        pass
        # for skill_data in self._skills_labels:
        #     shown_skill, _, xp_label = skill_data
        #     if skill.id == shown_skill.id:
        #         xp_label.text = (
        #             f"Current xp: {xp}. Next level: {skill.xp_to_next_level}"
        #         )

    def xp_gained(self, skill, xp):
        """Update xp label."""
        pass
        # for skill_data in self._skills_labels:
        #     shown_skill, _, xp_label = skill_data

        #     if skill.id == shown_skill.id:
        #         xp_label.text = (
        #             f"Current xp: {skill.xp}. Next level: {skill.xp_to_next_level}"
        #         )

    def goal_added(self, goal: Goal):
        goal_box = self._create_goal_box(goal)
        self.goals_box.add(goal_box)

    def goal_completed(self, goal: Goal, label, widget):
        label.enabled = False
        widget.enabled = False

        if goal.completed:
            widget.value = True
            return

        self.focus_app.complete_goal(goal.id)

    def startup(self) -> None:
        self.main_window = toga.Window()

        self._create_timer_box()
        self._create_goals_box()
        self._create_stats_box()
        self._create_skills_box()

        self.tabs_container = toga.OptionContainer(
            content=[
                ("Timer", self.timer_box),
                ("Stats", self.stats_box),
                ("Skills", self.skills_box),
                ("Goals", self.goals_box),
            ]
        )

        self.main_window.content = self.tabs_container
        self.main_window.show()

        self._counting_task = asyncio.create_task(self._update_timers())

    def _create_skills_box(self):
        @dataclass
        class SkillBox:
            skill_label: toga.Label
            xp_label: toga.Label
            next_level_label: toga.Label
            stats_label: toga.Label

        self.skills_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=10)
        )
        self.skills: dict[str, SkillBox] = {}

        for skill in self.focus_app.new_skills.values():
            skill_label = toga.Label(f"{skill.name.title()}: {skill.level}")
            xp_label = toga.Label(f"XP: {skill.xp}")
            next_level_label = toga.Label(f"XP to next level: {skill.xp_to_next_level}")
            stats = f"Main stat: {skill.main_stat.name.title()}"
            if skill.secondary_stat:
                stats += f" Secondary stat: {skill.secondary_stat.name.title()}"
            stats_label = toga.Label(stats)

            skill_box = toga.Box(
                style=Pack(direction=ROW, alignment=CENTER, padding=10)
            )
            skill_box.add(skill_label)
            skill_box.add(xp_label)
            skill_box.add(next_level_label)
            skill_box.add(stats_label)

            self.skills_box.add(skill_box)

            self.skills[skill.name] = SkillBox(
                skill_label=skill_label,
                xp_label=xp_label,
                next_level_label=next_level_label,
                stats_label=stats_label,
            )

    def _create_stats_box(self):
        self.stats_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=10)
        )
        self.stats: dict[str, toga.Label] = {}

        for stat in self.focus_app.stats.values():
            stat_label = toga.Label(f"{stat.name.title()}: {stat.value}")
            self.stats_box.add(stat_label)

            self.stats[stat.name] = stat_label

    def _create_goals_box(self):
        self.goals = {}
        self.goals_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        button_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=10)
        )
        self.add_goal_button = toga.Button(
            "New goal",
            on_press=self.add_goal,
            style=Pack(padding=10, alignment=CENTER),
        )
        button_box.add(self.add_goal_button)

        self.goals_box.add(button_box)
        self.goals_box.add(toga.Divider())

        for goal in self.focus_app.goals:
            goal_box = self._create_goal_box(goal)
            self.goals_box.add(goal_box)

    def _create_goal_box(self, goal: Goal):
        goal_box = toga.Box(style=Pack(direction=ROW, padding=10))
        label = toga.Label(
            goal.title,
            style=Pack(direction=COLUMN, padding=10, flex=20),
        )
        goal_box.add(label)

        dif_label = toga.Label(
            goal.difficulty,
            style=Pack(direction=COLUMN, padding=10, flex=20),
        )

        goal_box.add(dif_label)

        skill = self.focus_app.skills_repository.get_skill_by_id(goal.skill_id)

        skill_label = toga.Label(
            skill.name,
            style=Pack(direction=COLUMN, padding=10, flex=20),
        )

        goal_box.add(skill_label)

        def _goal_completed(widget):
            self.goal_completed(goal, label, widget)
            widget.enabled = False
            label.enabled = False

        completed_box = toga.Box(
            style=Pack(direction=COLUMN),
            children=[
                toga.Switch(
                    "Completed",
                    value=goal.completed,
                    on_change=_goal_completed,
                    style=Pack(padding=10, flex=33),
                )
            ],
        )
        goal_box.add(completed_box)

        return goal_box

    def _create_timer_box(self):
        self.timer_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=10)
        )
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
        self.timer_box.add(self.timer_label)

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

        button_box.add(self.pause_button)
        button_box.add(self.start_button)
        self.timer_box.add(button_box)
        self.skills_selection_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=10)
        )
        skills: list[str] = [skill.name for skill in self.focus_app.skills.values()]
        self.skill_selection = toga.Selection(
            items=skills, on_change=self.change_selected_skill
        )
        self.skill_selection.value = skills[0]
        self.skills_selection_box.add(self.skill_selection)

        self.timer_box.add(self.skills_selection_box)
        self.total_focused_time_label = toga.Label(
            "Total focused time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        self.timer_box.add(self.total_focused_time_label)
        self.total_break_time_label = toga.Label(
            "Total break time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        self.timer_box.add(self.total_break_time_label)

        self.earned_break_time_label = toga.Label(
            "Earned break time: 0 minutes", style=Pack(padding=10, alignment=CENTER)
        )
        self.timer_box.add(self.earned_break_time_label)

    def change_selected_skill(self, widget):
        if not self.focus_app.set_current_skill(widget.value):
            widget.value = self.focus_app.current_skill.name

    async def add_goal(self, widget):
        """Show a `Dialog` for input."""
        dialog = NewGoalDialog(title="Add a new goal", focus_app=self.focus_app)
        dialog.show()
        result = await dialog

        print("result is", result)
        if result == "Save":
            self.focus_app.add_goal(
                Goal(
                    title=dialog.title_input.value,
                    description=dialog.description_input.value,
                    difficulty=dialog.difficulty_selection.value,
                    skill_id=self.focus_app.skills[dialog.skill_selection.value].id,
                )
            )

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
            skill = self.focus_app.skills[skill.name]
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
