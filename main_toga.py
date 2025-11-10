"""Focus!

An application to help you with focusing (and resting).

Start the focused time!
Earn break time!
Rest!

"""

import asyncio
import os
import platform
from dataclasses import dataclass

import toga
from toga.style.pack import CENTER, COLUMN, ROW, Pack

from conf import PRIORITY_COLORS
from domain import Goal
from enums import Difficulty, Priority
from focus import Focus
from services import GoalsService, SkillsService
from signals import goal_added, level_gained, xp_gained
from timer import duration_from_seconds


class NewSkillDialog(toga.Window):
    def __init__(self, title: str, focus_app: "FocusApp"):
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

        name_label = toga.Label("Skill name:", style=common_style)
        self.name_input = toga.TextInput(style=common_style)
        description_label = toga.Label("Skill description:", style=common_style)
        self.description_input = toga.MultilineTextInput()
        main_stat_label = toga.Label(" Main stat:", style=common_style)
        self.main_stat_selection = toga.Selection(
            items=[stat.name.title() for stat in focus_app.focus_app.stats.values()],
            style=common_style,
        )
        secondary_stat_label = toga.Label("Secondary stat:", style=Pack(padding=(0, 5)))
        self.secondary_stat_selection = toga.Selection(
            items=[stat.name.title() for stat in focus_app.focus_app.stats.values()],
            style=common_style,
        )

        self.content.add(name_label)
        self.content.add(self.name_input)
        self.content.add(description_label)
        self.content.add(self.description_input)
        self.content.add(main_stat_label)
        self.content.add(self.main_stat_selection)
        self.content.add(secondary_stat_label)
        self.content.add(self.secondary_stat_selection)
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


class LevelUpDialog(toga.Window):
    def __init__(self, title: str, skill, previous_level: int, xp_gained: int):
        super().__init__(title=title, resizable=False, size=(450, 350))

        self.skill = skill

        self.ok_button = toga.Button(
            "Awesome!",
            on_press=self.on_accept,
            style=Pack(padding=15, alignment=CENTER),
        )

        self.content = toga.Box(
            style=Pack(direction=COLUMN, padding=20, alignment=CENTER)
        )

        # Header
        level_label = toga.Label(
            "🎉 Level Up! 🎉",
            style=Pack(
                font_size=20, font_weight="bold", padding_bottom=15, alignment=CENTER
            ),
        )

        # Skill name and level progression
        skill_label = toga.Label(
            f"{skill.name.title()}",
            style=Pack(
                font_size=16, font_weight="bold", padding_bottom=5, alignment=CENTER
            ),
        )
        level_progress_label = toga.Label(
            f"Level {previous_level} → Level {skill.level}",
            style=Pack(
                font_size=14, color="#2E7D32", padding_bottom=15, alignment=CENTER
            ),
        )

        # XP gained
        xp_label = toga.Label(
            f"🌟 +{xp_gained} XP gained!",
            style=Pack(
                font_size=12, color="#1976D2", padding_bottom=10, alignment=CENTER
            ),
        )

        # Stats increased
        stats_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=CENTER))
        stats_header = toga.Label(
            "📈 Stats Increased:",
            style=Pack(
                font_size=12, font_weight="bold", padding_bottom=5, alignment=CENTER
            ),
        )
        stats_box.add(stats_header)

        main_stat_label = toga.Label(
            f"• {skill.main_stat.name.title()}: +1",
            style=Pack(font_size=11, padding_bottom=2, alignment=CENTER),
        )
        stats_box.add(main_stat_label)

        if skill.secondary_stat:
            secondary_stat_label = toga.Label(
                f"• {skill.secondary_stat.name.title()}: +1",
                style=Pack(font_size=11, padding_bottom=2, alignment=CENTER),
            )
            stats_box.add(secondary_stat_label)

        # Progress to next level
        progress_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10, alignment=CENTER)
        )
        progress_header = toga.Label(
            "🎯 Next Level Progress:",
            style=Pack(
                font_size=12, font_weight="bold", padding_bottom=5, alignment=CENTER
            ),
        )
        progress_box.add(progress_header)

        progress_label = toga.Label(
            f"{skill.xp} / {skill.xp + skill.xp_to_next_level} XP",
            style=Pack(font_size=11, padding_bottom=5, alignment=CENTER),
        )
        progress_box.add(progress_label)

        # Progress bar
        total_xp_for_level = skill.xp + skill.xp_to_next_level
        current_progress = (
            skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0
        )
        progress_bar = toga.ProgressBar(
            max=1.0, value=current_progress, style=Pack(padding=(5, 20), width=300)
        )
        progress_box.add(progress_bar)

        # Add all elements to content
        self.content.add(level_label)
        self.content.add(skill_label)
        self.content.add(level_progress_label)
        self.content.add(xp_label)
        self.content.add(stats_box)
        self.content.add(progress_box)
        self.content.add(self.ok_button)

        self.future = self.app.loop.create_future()

    def on_accept(self, widget, **kwargs):
        self.future.set_result("OK")
        self.close()

    def __await__(self):
        return self.future.__await__()


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
            items=[skill.name for skill in focus_app.new_skills.values()],
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

        level_gained.connect(self._on_level_gained)
        xp_gained.connect(self.xp_gained)
        goal_added.connect(self.goal_added)

        self.notified = False
        "Notify when break time runs out. Only once."
        
        self.stats_expanded = True
        "Track whether session statistics are expanded or collapsed"

    def _on_level_gained(self, skill, previous_level, xp_gained):
        """Wrapper to handle async level_gained callback."""
        task = asyncio.create_task(self.level_gained(skill, previous_level, xp_gained))
        # Store reference to prevent garbage collection
        self._level_up_tasks = getattr(self, '_level_up_tasks', set())
        self._level_up_tasks.add(task)
        task.add_done_callback(self._level_up_tasks.discard)

    async def level_gained(self, skill, previous_level, xp_gained):
        box = self.skills[skill.name]
        box.skill_label.text = f"{skill.name.title()}: Level {skill.level}"
        box.xp_label.text = f"XP: {skill.xp} "
        box.next_level_label.text = f"XP to next level: {skill.xp_to_next_level}"

        # Update progress bar
        total_xp_for_level = skill.xp + skill.xp_to_next_level
        current_progress = (
            skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0
        )
        box.progress_bar.value = current_progress

        # Update level badge
        box.level_badge.text = f"LV.{skill.level}"

        # Update colors based on new level
        def get_level_colors(level):
            if level >= 20:
                return {"bg": "#e8f5e8", "border": "#4CAF50", "accent": "#2E7D32"}
            elif level >= 15:
                return {"bg": "#fff3e0", "border": "#FF9800", "accent": "#E65100"}
            elif level >= 10:
                return {"bg": "#e3f2fd", "border": "#2196F3", "accent": "#0D47A1"}
            elif level >= 5:
                return {"bg": "#f3e5f5", "border": "#9C27B0", "accent": "#4A148C"}
            else:
                return {"bg": "#f8f9fa", "border": "#9E9E9E", "accent": "#424242"}

        colors = get_level_colors(skill.level)
        box.skill_card.style.background_color = colors["bg"]
        box.level_badge.style.background_color = colors["accent"]

        # Update main stat card
        self._update_stat_card(skill.main_stat.name, skill.main_stat.value)

        if skill.secondary_stat:
            # Update secondary stat card
            self._update_stat_card(
                skill.secondary_stat.name, skill.secondary_stat.value
            )

        # Show level up dialog
        dialog = LevelUpDialog(
            title="Level Up!",
            skill=skill,
            previous_level=previous_level,
            xp_gained=xp_gained,
        )
        dialog.show()
        await dialog

    def xp_gained(self, skill, xp_earned):
        """Update xp label."""
        box = self.skills[skill.name]
        box.xp_label.text = f"XP: {skill.xp} "
        box.next_level_label.text = f"XP to next level: {skill.xp_to_next_level}"

        # Update progress bar
        total_xp_for_level = skill.xp + skill.xp_to_next_level
        current_progress = (
            skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0
        )
        box.progress_bar.value = current_progress

    def goal_added(self, goal: Goal):
        goal_box = self._create_goal_box(goal)
        # Find the scroll container and add to its content
        goals_scroll = self.goals_box.children[-1]  # Last child is the scroll container
        goals_scroll.content.add(goal_box)
        # Add spacing after new goal
        goals_scroll.content.add(toga.Box(style=Pack(height=5)))

    def goal_completed(self, goal: Goal, label, widget):
        label.enabled = False
        widget.enabled = False

        if goal.completed:
            widget.value = True
            return

        GoalsService().complete_goal(goal.id)

    def startup(self) -> None:
        self.main_window = toga.Window(
            size=(800, 600),        # Initial size
            resizable=True          # Allow user resizing
        )

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

        # Main container
        self.skills_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.skills: dict[str, SkillBox] = {}

        # Button at the top (non-scrollable)
        button_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=10)
        )
        self.add_skill_button = toga.Button(
            "New skill",
            on_press=self.add_skill,
            style=Pack(padding=10, alignment=CENTER),
        )
        button_box.add(self.add_skill_button)
        self.skills_box.add(button_box)
        self.skills_box.add(toga.Divider())

        # Scrollable container for skills
        self.skills_scroll_container = toga.ScrollContainer(
            style=Pack(direction=COLUMN, flex=1)
        )

        # Box inside scroll container to hold skills
        self.skills_list_box = toga.Box(style=Pack(direction=COLUMN, padding=5))

        self.skills_scroll_container.content = self.skills_list_box
        self.skills_box.add(self.skills_scroll_container)

        for skill in self.focus_app.new_skills.values():
            skill_box = self._create_skill_box(skill)
            self.skills_list_box.add(skill_box)

    def _create_skill_box(self, skill):
        @dataclass
        class SkillBox:
            skill_label: toga.Label
            xp_label: toga.Label
            next_level_label: toga.Label
            stats_label: toga.Label
            progress_bar: toga.ProgressBar
            level_badge: toga.Label
            skill_card: toga.Box

        skill_label = toga.Label(
            f"{skill.name.title()}: Level {skill.level}",
            style=Pack(font_size=16, font_weight="bold", padding_bottom=5),
        )
        xp_label = toga.Label(
            f"XP: {skill.xp}", style=Pack(font_size=12, color="#666666")
        )
        next_level_label = toga.Label(
            f"XP to next level: {skill.xp_to_next_level}",
            style=Pack(font_size=12, color="#666666"),
        )
        stats = f"Main stat: {skill.main_stat.name.title()}"
        if skill.secondary_stat:
            stats += f" Secondary stat: {skill.secondary_stat.name.title()}"
        stats_label = toga.Label(
            stats, style=Pack(font_size=11, color="#888888", padding_top=5)
        )

        # Calculate progress percentage for current level
        total_xp_for_level = skill.xp + skill.xp_to_next_level
        current_progress = (
            skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0
        )

        # Determine color scheme based on skill level
        def get_level_colors(level):
            if level >= 20:
                return {
                    "bg": "#e8f5e8",
                    "border": "#4CAF50",
                    "accent": "#2E7D32",
                }  # Green - Master
            elif level >= 15:
                return {
                    "bg": "#fff3e0",
                    "border": "#FF9800",
                    "accent": "#E65100",
                }  # Orange - Expert
            elif level >= 10:
                return {
                    "bg": "#e3f2fd",
                    "border": "#2196F3",
                    "accent": "#0D47A1",
                }  # Blue - Advanced
            elif level >= 5:
                return {
                    "bg": "#f3e5f5",
                    "border": "#9C27B0",
                    "accent": "#4A148C",
                }  # Purple - Intermediate
            else:
                return {
                    "bg": "#f8f9fa",
                    "border": "#9E9E9E",
                    "accent": "#424242",
                }  # Gray - Beginner

        colors = get_level_colors(skill.level)

        # Create progress bar with level-based color
        progress_bar = toga.ProgressBar(
            max=1.0, value=current_progress, style=Pack(padding=(5, 0), width=200)
        )

        # Add level badge
        level_badge = toga.Label(
            f"LV.{skill.level}",
            style=Pack(
                font_size=10,
                color="white",
                background_color=colors["accent"],
                padding=(2, 6),
                text_align="center",
            ),
        )

        # Create card-style container with level-based colors
        skill_card = toga.Box(
            style=Pack(
                direction=COLUMN,
                padding=15,
                background_color=colors["bg"],
                text_align="left",
            )
        )

        # Add visual separator between cards
        skill_container = toga.Box(style=Pack(direction=COLUMN, padding=(5, 10)))

        # Create header with skill name and level badge
        header_box = toga.Box(style=Pack(direction=ROW, padding_bottom=5))

        # Use flex to push badge to the right
        skill_label.style.flex = 1
        level_badge.style.flex = 0

        header_box.add(skill_label)
        header_box.add(level_badge)

        # Add all elements vertically in the card
        skill_card.add(header_box)
        skill_card.add(progress_bar)
        skill_card.add(xp_label)
        skill_card.add(next_level_label)
        skill_card.add(stats_label)

        skill_container.add(skill_card)

        self.skills[skill.name] = SkillBox(
            skill_label=skill_label,
            xp_label=xp_label,
            next_level_label=next_level_label,
            stats_label=stats_label,
            progress_bar=progress_bar,
            level_badge=level_badge,
            skill_card=skill_card,
        )
        return skill_container

    def _create_stats_box(self):
        self.stats_box = toga.Box(style=Pack(direction=COLUMN, padding=15))
        self.stats: dict[str, toga.Label] = {}

        # Create scrollable container for stats
        stats_scroll_container = toga.ScrollContainer(
            style=Pack(direction=COLUMN, flex=1)
        )

        # Box inside scroll container to hold stats
        stats_list_box = toga.Box(style=Pack(direction=COLUMN, padding=5))

        stats_scroll_container.content = stats_list_box
        self.stats_box.add(stats_scroll_container)

        for stat in self.focus_app.stats.values():
            stat_card = self._create_stat_card(stat)
            stats_list_box.add(stat_card)
            # Add spacing between cards
            stats_list_box.add(toga.Box(style=Pack(height=8)))

    def _create_stat_card(self, stat):
        """Create an enhanced stat card with progress bars and visual indicators."""

        # Define stat properties and color schemes
        stat_info = self._get_stat_info(stat.name)
        max_value = stat_info["max"]
        colors = stat_info["colors"]
        icon = stat_info["icon"]
        description = stat_info["description"]

        # Calculate progress percentage
        progress = min(stat.value / max_value, 1.0) if max_value > 0 else 0

        # Get color based on value range
        if progress >= 0.8:
            color_scheme = colors["high"]
        elif progress >= 0.5:
            color_scheme = colors["medium"]
        else:
            color_scheme = colors["low"]

        # Create card container
        stat_card = toga.Box(
            style=Pack(
                direction=COLUMN, padding=15, background_color=color_scheme["bg"]
            )
        )

        # Header with icon, name, and value
        header_box = toga.Box(style=Pack(direction=ROW, padding_bottom=8))

        # Icon and name section
        name_section = toga.Box(style=Pack(direction=ROW, flex=1))

        icon_label = toga.Label(
            icon,
            style=Pack(
                font_size=16, padding=(0, 8, 0, 0), color=color_scheme["accent"]
            ),
        )
        name_section.add(icon_label)

        stat_name_label = toga.Label(
            stat.name.title(),
            style=Pack(
                font_size=14, font_weight="bold", color=color_scheme["text"], flex=1
            ),
        )
        name_section.add(stat_name_label)
        header_box.add(name_section)

        # Value display
        value_label = toga.Label(
            str(stat.value),
            style=Pack(
                font_size=20,
                font_weight="bold",
                color=color_scheme["accent"],
                text_align="right",
            ),
        )
        header_box.add(value_label)

        # Progress bar
        progress_bar = toga.ProgressBar(
            max=1.0, value=progress, style=Pack(padding=(5, 0), width=250)
        )

        # Progress info
        progress_info = toga.Label(
            f"{stat.value} / {max_value}",
            style=Pack(font_size=11, color=color_scheme["secondary"], padding=(3, 0)),
        )

        # Description
        desc_label = toga.Label(
            description,
            style=Pack(
                font_size=10,
                color=color_scheme["secondary"],
                padding=(5, 0, 0, 0),
                text_align="left",
            ),
        )

        # Add all elements to card
        stat_card.add(header_box)
        stat_card.add(progress_bar)
        stat_card.add(progress_info)
        stat_card.add(desc_label)

        # Create container with subtle border effect
        stat_container = toga.Box(style=Pack(direction=COLUMN, padding=(3, 8)))
        stat_container.add(stat_card)

        # Store references for updates
        self.stats[stat.name] = {
            "name_label": stat_name_label,
            "value_label": value_label,
            "progress_bar": progress_bar,
            "progress_info": progress_info,
            "card": stat_card,
            "container": stat_container,
        }

        return stat_container

    def _get_stat_info(self, stat_name):
        """Get stat-specific information including colors, icons, and descriptions."""
        stat_configs = {
            "intellect": {
                "max": 50,
                "icon": "🧠",
                "description": "Mental capacity and problem-solving ability",
                "colors": {
                    "low": {
                        "bg": "#f8f9fa",
                        "accent": "#6f42c1",
                        "text": "#495057",
                        "secondary": "#6c757d",
                    },
                    "medium": {
                        "bg": "#e8eaf6",
                        "accent": "#3f51b5",
                        "text": "#1a237e",
                        "secondary": "#5c6bc0",
                    },
                    "high": {
                        "bg": "#e1f5fe",
                        "accent": "#0277bd",
                        "text": "#01579b",
                        "secondary": "#0288d1",
                    },
                },
            },
            "willpower": {
                "max": 30,
                "icon": "💪",
                "description": "Mental strength and determination",
                "colors": {
                    "low": {
                        "bg": "#fff3e0",
                        "accent": "#f57c00",
                        "text": "#e65100",
                        "secondary": "#ff9800",
                    },
                    "medium": {
                        "bg": "#fff8e1",
                        "accent": "#ffa000",
                        "text": "#ff6f00",
                        "secondary": "#ffb300",
                    },
                    "high": {
                        "bg": "#fffde7",
                        "accent": "#fbc02d",
                        "text": "#f57f17",
                        "secondary": "#fdd835",
                    },
                },
            },
            "dexterity": {
                "max": 40,
                "icon": "🤹",
                "description": "Hand coordination and precision",
                "colors": {
                    "low": {
                        "bg": "#e8f5e8",
                        "accent": "#388e3c",
                        "text": "#1b5e20",
                        "secondary": "#4caf50",
                    },
                    "medium": {
                        "bg": "#f1f8e9",
                        "accent": "#689f38",
                        "text": "#33691e",
                        "secondary": "#8bc34a",
                    },
                    "high": {
                        "bg": "#f9fbe7",
                        "accent": "#9e9d24",
                        "text": "#827717",
                        "secondary": "#cddc39",
                    },
                },
            },
            "vitality": {
                "max": 25,
                "icon": "❤️",
                "description": "Physical health and energy",
                "colors": {
                    "low": {
                        "bg": "#ffebee",
                        "accent": "#d32f2f",
                        "text": "#b71c1c",
                        "secondary": "#f44336",
                    },
                    "medium": {
                        "bg": "#fce4ec",
                        "accent": "#c2185b",
                        "text": "#880e4f",
                        "secondary": "#e91e63",
                    },
                    "high": {
                        "bg": "#f3e5f5",
                        "accent": "#7b1fa2",
                        "text": "#4a148c",
                        "secondary": "#9c27b0",
                    },
                },
            },
            "charisma": {
                "max": 35,
                "icon": "✨",
                "description": "Social influence and persuasion",
                "colors": {
                    "low": {
                        "bg": "#fce4ec",
                        "accent": "#ad1457",
                        "text": "#880e4f",
                        "secondary": "#e91e63",
                    },
                    "medium": {
                        "bg": "#f8bbd9",
                        "accent": "#c2185b",
                        "text": "#ad1457",
                        "secondary": "#e91e63",
                    },
                    "high": {
                        "bg": "#f48fb1",
                        "accent": "#880e4f",
                        "text": "#4a148c",
                        "secondary": "#ad1457",
                    },
                },
            },
            "strength": {
                "max": 30,
                "icon": "🏋️",
                "description": "Physical power and endurance",
                "colors": {
                    "low": {
                        "bg": "#efebe9",
                        "accent": "#5d4037",
                        "text": "#3e2723",
                        "secondary": "#795548",
                    },
                    "medium": {
                        "bg": "#d7ccc8",
                        "accent": "#6d4c41",
                        "text": "#4e342e",
                        "secondary": "#8d6e63",
                    },
                    "high": {
                        "bg": "#bcaaa4",
                        "accent": "#4e342e",
                        "text": "#3e2723",
                        "secondary": "#6d4c41",
                    },
                },
            },
            "wisdom": {
                "max": 45,
                "icon": "🦉",
                "description": "Experience and sound judgment",
                "colors": {
                    "low": {
                        "bg": "#e0f2f1",
                        "accent": "#00695c",
                        "text": "#004d40",
                        "secondary": "#009688",
                    },
                    "medium": {
                        "bg": "#b2dfdb",
                        "accent": "#00796b",
                        "text": "#00695c",
                        "secondary": "#26a69a",
                    },
                    "high": {
                        "bg": "#80cbc4",
                        "accent": "#004d40",
                        "text": "#00251a",
                        "secondary": "#00695c",
                    },
                },
            },
        }

        # Return default config if stat not found
        return stat_configs.get(
            stat_name.lower(),
            {
                "max": 20,
                "icon": "📊",
                "description": "Character attribute",
                "colors": {
                    "low": {
                        "bg": "#f5f5f5",
                        "accent": "#616161",
                        "text": "#424242",
                        "secondary": "#757575",
                    },
                    "medium": {
                        "bg": "#eeeeee",
                        "accent": "#424242",
                        "text": "#212121",
                        "secondary": "#616161",
                    },
                    "high": {
                        "bg": "#e0e0e0",
                        "accent": "#212121",
                        "text": "#000000",
                        "secondary": "#424242",
                    },
                },
            },
        )

    def _update_stat_card(self, stat_name, new_value):
        """Update a stat card with new value and visual changes."""
        if stat_name not in self.stats:
            return

        stat_components = self.stats[stat_name]
        stat_info = self._get_stat_info(stat_name)
        max_value = stat_info["max"]
        colors = stat_info["colors"]

        # Calculate new progress
        progress = min(new_value / max_value, 1.0) if max_value > 0 else 0

        # Get new color scheme
        if progress >= 0.8:
            color_scheme = colors["high"]
        elif progress >= 0.5:
            color_scheme = colors["medium"]
        else:
            color_scheme = colors["low"]

        # Update value label
        stat_components["value_label"].text = str(new_value)
        stat_components["value_label"].style.color = color_scheme["accent"]

        # Update progress bar
        stat_components["progress_bar"].value = progress

        # Update progress info
        stat_components["progress_info"].text = f"{new_value} / {max_value}"
        stat_components["progress_info"].style.color = color_scheme["secondary"]

        # Update card background color
        stat_components["card"].style.background_color = color_scheme["bg"]

        # Update name label color
        stat_components["name_label"].style.color = color_scheme["text"]

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

        # Create scrollable container for goals list
        goals_list_box = toga.Box(style=Pack(direction=COLUMN, padding=5))

        # Get goals sorted by priority using service layer
        sorted_goals = GoalsService().get_goals_by_priority(completed=False)

        for goal in sorted_goals:
            goal_box = self._create_goal_box(goal)
            goals_list_box.add(goal_box)
            # Add spacing between goals
            goals_list_box.add(toga.Box(style=Pack(height=5)))

        # Wrap goals list in scroll container that uses available space
        goals_scroll = toga.ScrollContainer(
            content=goals_list_box, style=Pack(flex=1, padding=5)
        )

        self.goals_box.add(goals_scroll)

    def _create_goal_box(self, goal: Goal):
        # Main container with card-like appearance
        goal_box = toga.Box(
            style=Pack(
                direction=ROW,
                padding=(15, 10, 15, 10),  # top, right, bottom, left
                background_color="#f8f9fa",
            )
        )

        # Title section with better typography
        title_box = toga.Box(style=Pack(direction=COLUMN, padding=(5, 10), flex=3))
        title_label = toga.Label(
            goal.title,
            style=Pack(padding=(0, 5, 5, 0), font_weight="bold", font_size=14),
        )
        title_box.add(title_label)
        goal_box.add(title_box)

        # Priority section with dropdown selector
        priority_box = toga.Box(style=Pack(direction=COLUMN, padding=(5, 10), flex=1))
        
        def _priority_changed(widget):
            """Handle priority change for this goal"""
            new_priority = Priority(widget.value.lower())
            GoalsService().update_goal_priority(goal.id, new_priority)
            # Refresh the goals list to maintain priority ordering
            self._refresh_goals_list()
        
        priority_selection = toga.Selection(
            items=[p.value.title() for p in Priority],
            value=goal.priority.value.title(),
            on_change=_priority_changed,
            style=Pack(padding=(2, 5), font_size=11, width=80),
        )
        priority_box.add(priority_selection)
        goal_box.add(priority_box)

        # Difficulty section with visual indicator
        diff_box = toga.Box(style=Pack(direction=COLUMN, padding=(5, 10), flex=1))
        difficulty_color = self._get_difficulty_color(goal.difficulty)
        dif_label = toga.Label(
            goal.difficulty.title(),
            style=Pack(
                padding=(0, 5), font_size=12, color=difficulty_color, font_weight="bold"
            ),
        )
        diff_box.add(dif_label)
        goal_box.add(diff_box)

        # Skill section
        skill = self.focus_app.new_skills[goal.main_skill.name]
        skill_box = toga.Box(style=Pack(direction=COLUMN, padding=(5, 10), flex=2))
        skill_label = toga.Label(
            skill.name,
            style=Pack(padding=(0, 5), font_size=12, color="#6c757d"),
        )
        skill_box.add(skill_label)
        goal_box.add(skill_box)

        # Completion section
        def _goal_completed(widget):
            self.focus_app.complete_goal(goal.id)
            self.goal_completed(goal, title_label, widget)
            widget.enabled = False
            title_label.enabled = False

        completed_box = toga.Box(
            style=Pack(direction=COLUMN, padding=(5, 10), flex=1),
            children=[
                toga.Switch(
                    "Done",
                    value=goal.completed,
                    on_change=_goal_completed,
                    style=Pack(padding=(5, 0)),
                )
            ],
        )
        goal_box.add(completed_box)

        return goal_box

    def _get_difficulty_color(self, difficulty):
        """Return color code based on difficulty level"""
        colors = {
            "easy": "#28a745",  # Green
            "medium": "#ffc107",  # Yellow
            "hard": "#dc3545",  # Red
        }
        return colors.get(difficulty.lower(), "#6c757d")

    def _get_priority_color(self, priority):
        """Return color code based on priority level"""
        return PRIORITY_COLORS.get(priority.value.lower(), "#6c757d")

    def _refresh_goals_list(self):
        """Refresh the goals list with updated priorities"""
        # Get the scroll container (last child of goals_box)
        goals_scroll = self.goals_box.children[-1]
        
        # Clear existing goals
        goals_scroll.content.clear()
        
        # Re-add goals sorted by priority
        sorted_goals = GoalsService().get_goals_by_priority(completed=False)
        for goal in sorted_goals:
            goal_box = self._create_goal_box(goal)
            goals_scroll.content.add(goal_box)
            # Add spacing between goals
            goals_scroll.content.add(toga.Box(style=Pack(height=5)))

    def _create_timer_box(self):
        # Main container for timer tab
        self.timer_box = toga.Box(style=Pack(direction=COLUMN, padding=0))
        
        # Create scrollable container for all timer content
        timer_scroll_container = toga.ScrollContainer(
            style=Pack(direction=COLUMN, flex=1)
        )
        
        # Content box inside scroll container
        timer_content_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=15)
        )

        # Enhanced timer display container with card-like design
        timer_card = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=20,
                background_color="#f8f9fa",
            )
        )

        # State indicator label
        self.state_indicator = toga.Label(
            "Ready to Focus",
            style=Pack(
                alignment=CENTER,
                font_size=16,
                font_weight="bold",
                color="#6c757d",
                padding_bottom=10,
            ),
        )
        timer_card.add(self.state_indicator)

        # Enhanced timer label with better styling
        self.timer_label = toga.Label(
            "00:00",
            style=Pack(
                padding=(10, 20),
                alignment=CENTER,
                font_size=85,
                font_weight="bold",
                color="#2c3e50",
                text_align=CENTER,
            ),
        )
        timer_card.add(self.timer_label)

        # Progress indicator for break time usage
        self.break_progress = toga.ProgressBar(
            max=1.0, value=0.0, style=Pack(width=300, padding=(10, 20))
        )

        self.progress_label = toga.Label(
            "Break time progress",
            style=Pack(font_size=12, color="#6c757d", padding=(5, 0), alignment=CENTER),
        )

        timer_card.add(self.progress_label)
        timer_card.add(self.break_progress)

        timer_content_box.add(timer_card)

        # Enhanced button container
        button_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding=15))

        self.pause_button = toga.Button(
            "⏸ Pause",
            on_press=self.toggle_pause,
            style=Pack(
                padding=(15, 25),
                alignment=CENTER,
                background_color="#ffc107",
                color="white",
                font_size=14,
                font_weight="bold",
            ),
        )

        self.cancel_button = toga.Button(
            "❌ Cancel",
            on_press=self.cancel_session,
            style=Pack(
                padding=(15, 25),
                alignment=CENTER,
                background_color="#dc3545",
                color="white",
                font_size=14,
                font_weight="bold",
                visibility="hidden",  # Initially hidden
            ),
        )

        self.start_button = toga.Button(
            "🎯 Focus!",
            on_press=self.toggle_timers,
            style=Pack(
                padding=(15, 25),
                alignment=CENTER,
                background_color="#28a745",
                color="white",
                font_size=14,
                font_weight="bold",
            ),
        )

        button_box.add(self.pause_button)
        button_box.add(self.cancel_button)
        button_box.add(self.start_button)
        timer_content_box.add(button_box)
        # Enhanced skill selection section
        self.skills_selection_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=15)
        )

        # Skill selection label
        skill_label = toga.Label(
            "🎯 Current Skill",
            style=Pack(
                font_size=14,
                font_weight="bold",
                color="#495057",
                padding_bottom=10,
                alignment=CENTER,
            ),
        )
        self.skills_selection_box.add(skill_label)

        # Recent skills quick access buttons (show first 8 skills if no recent usage yet)
        recent_skills = SkillsService().get_recent_skills(8)
        if not recent_skills:
            # Fallback: show first 8 skills if no usage tracking yet
            all_skills = list(self.focus_app.new_skills.values())
            recent_skills = all_skills[:8]
        
        if recent_skills:
            recent_label = toga.Label(
                "Quick Access:",
                style=Pack(
                    font_size=12,
                    color="#6c757d",
                    padding_bottom=5,
                    alignment=CENTER,
                ),
            )
            self.skills_selection_box.add(recent_label)
            
            # Create grid container for buttons (2 rows of 4 buttons each)
            self.recent_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=(5, 0)))
            
            # Split skills into rows of 4
            for row_start in range(0, min(len(recent_skills), 8), 4):
                row_skills = recent_skills[row_start:row_start + 4]
                row_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding=(2, 0)))
                
                for skill in row_skills:
                    btn = toga.Button(
                        skill.name.title()[:8],  # Truncate long names
                        on_press=lambda w, s=skill.name: self.select_recent_skill(s),
                        style=Pack(
                            padding=(2, 5), 
                            font_size=11,
                            background_color="#e9ecef",
                            color="#495057"
                        ),
                    )
                    row_box.add(btn)
                
                self.recent_box.add(row_box)
            
            self.skills_selection_box.add(self.recent_box)

        skills: list[str] = [
            skill.name.title() for skill in self.focus_app.new_skills.values()
        ]

        # Enhanced skill selection with card-like container
        skill_card = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=15,
                background_color="#e9ecef",
            )
        )

        self.skill_selection = toga.Selection(
            items=skills,
            on_change=self.change_selected_skill,
            style=Pack(padding=10, font_size=14, width=250),
        )

        if skills:
            self.skill_selection.value = skills[0]

        skill_card.add(self.skill_selection)
        self.skills_selection_box.add(skill_card)
        timer_content_box.add(self.skills_selection_box)
        # Enhanced statistics section
        stats_container = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=15)
        )

        stats_card = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=20,
                background_color="#f1f3f4",
            )
        )

        # Collapsible stats header with toggle button
        stats_header_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding_bottom=10))
        
        self.stats_toggle_button = toga.Button(
            "▼ 📊 Session Statistics",
            on_press=self.toggle_stats_visibility,
            style=Pack(
                font_size=14,
                font_weight="bold",
                color="#495057",
                background_color="transparent",
                alignment=CENTER,
            ),
        )
        stats_header_box.add(self.stats_toggle_button)
        stats_card.add(stats_header_box)

        # Create a collapsible container for stats
        self.stats_content = toga.Box(style=Pack(direction=COLUMN, padding=5))

        self.total_focused_time_label = toga.Label(
            "🎯 Total focused time: 00:00",
            style=Pack(padding=5, alignment=CENTER, font_size=12, color="#28a745"),
        )
        self.stats_content.add(self.total_focused_time_label)

        self.total_break_time_label = toga.Label(
            "☕ Total break time: 00:00",
            style=Pack(padding=5, alignment=CENTER, font_size=12, color="#007bff"),
        )
        self.stats_content.add(self.total_break_time_label)

        self.earned_break_time_label = toga.Label(
            "⏰ Earned break time: 0 minutes",
            style=Pack(padding=5, alignment=CENTER, font_size=12, color="#6c757d"),
        )
        self.stats_content.add(self.earned_break_time_label)

        stats_card.add(self.stats_content)
        stats_container.add(stats_card)
        timer_content_box.add(stats_container)
        
        # Set content for scroll container and add to main timer box
        timer_scroll_container.content = timer_content_box
        self.timer_box.add(timer_scroll_container)

    def toggle_stats_visibility(self, widget):
        """Toggle visibility of session statistics section."""
        self.stats_expanded = not self.stats_expanded
        
        if self.stats_expanded:
            # Show stats content
            self.stats_content.style.visibility = "visible"
            self.stats_toggle_button.text = "▼ 📊 Session Statistics"
        else:
            # Hide stats content  
            self.stats_content.style.visibility = "hidden"
            self.stats_toggle_button.text = "▶ 📊 Session Statistics"

    def change_selected_skill(self, widget):
        if not self.focus_app.set_current_skill(widget.value.lower()):
            widget.value = self.focus_app.current_skill.name.title()
        else:
            # Mark skill as used when selected from dropdown
            skill = self.focus_app.new_skills[widget.value.lower()]
            SkillsService().mark_skill_as_used(skill.id)
            # Refresh quick access buttons
            self._refresh_recent_skills()

    def select_recent_skill(self, skill_name: str):
        """Handle quick-access skill selection from recent buttons."""
        if self.focus_app.set_current_skill(skill_name):
            self.skill_selection.value = skill_name.title()
            # Mark as used for tracking
            skill = self.focus_app.new_skills[skill_name]
            SkillsService().mark_skill_as_used(skill.id)
            # Refresh recent skills buttons
            self._refresh_recent_skills()

    async def add_skill(self, widget):
        """Show a `Dialog` for input."""
        dialog = NewSkillDialog(title="Add a new skill", focus_app=self)
        dialog.show()
        result = await dialog

        if result == "Save":
            self.focus_app.add_skill(
                name=dialog.name_input.value,
                main_stat_name=dialog.main_stat_selection.value,
                secondary_stat_name=dialog.secondary_stat_selection.value,
            )
            self.skills_list_box.add(
                self._create_skill_box(
                    self.focus_app.new_skills[dialog.name_input.value]
                )
            )
            self.skill_selection.items = [
                skill.name.title() for skill in self.focus_app.new_skills.values()
            ]

    async def add_goal(self, widget):
        """Show a `Dialog` for input."""
        dialog = NewGoalDialog(title="Add a new goal", focus_app=self.focus_app)
        dialog.show()
        result = await dialog

        if result == "Save":
            self.focus_app.add_goal(
                Goal(
                    title=dialog.title_input.value,
                    description=dialog.description_input.value,
                    difficulty=dialog.difficulty_selection.value,
                    main_skill=self.focus_app.new_skills[dialog.skill_selection.value],
                )
            )

    def toggle_pause(self, widget) -> None:
        if self.focus_app.paused:
            self.focus_app.unpause()
            # Update visual state when unpausing
            self.pause_button.text = "⏸ Pause"
            self.pause_button.style.background_color = "#ffc107"
            if self.focus_app.focusing:
                self.state_indicator.text = "🎯 Focusing"
                self.state_indicator.style.color = "#28a745"
                self.timer_label.style.color = "#28a745"
                self.cancel_button.style.visibility = "visible"
            elif self.focus_app.resting:
                self.state_indicator.text = "☕ On Break"
                self.state_indicator.style.color = "#007bff"
                self.timer_label.style.color = "#007bff"
                self.cancel_button.style.visibility = "hidden"
        else:
            self.focus_app.pause()
            # Update visual state when pausing
            self.pause_button.text = "▶ Resume"
            self.pause_button.style.background_color = "#17a2b8"
            self.state_indicator.text = "⏸ Paused"
            self.state_indicator.style.color = "#6c757d"
            self.timer_label.style.color = "#6c757d"
            self.cancel_button.style.visibility = "hidden"

    def cancel_session(self, widget) -> None:
        """Cancel the current focus session without awarding XP."""
        if self.focus_app.focusing:
            self.focus_app.cancel()
            # Reset UI to initial "Ready to Focus" state
            self.state_indicator.text = "Ready to Focus"
            self.state_indicator.style.color = "#6c757d"
            self.timer_label.text = "00:00"
            self.timer_label.style.color = "#2c3e50"
            self.start_button.text = "🎯 Focus!"
            self.start_button.style.background_color = "#28a745"
            self.pause_button.text = "⏸ Pause"
            self.pause_button.style.background_color = "#ffc107"
            self.progress_label.text = "Break time used"
            self.break_progress.value = 0.0

    def toggle_timers(self, widget) -> None:
        if not self.focus_app.started or self.focus_app.resting:
            self.focus_app.focus()
            self.earned_break_time_label.text = f"⏰ Earned break time: {self.focus_app.earned_break_time // 60} minutes"
            # Update visual state for focus mode
            self.start_button.text = "☕ Break"
            self.start_button.style.background_color = "#007bff"
            self.state_indicator.text = "🎯 Focusing"
            self.state_indicator.style.color = "#28a745"
            self.timer_label.style.color = "#28a745"
            self.cancel_button.style.visibility = "visible"

            if self.focus_app.earned_break_time < 0:
                self.timer_label.style.color = "#dc3545"
        else:
            self.notified = False
            self._enter_break()

    def _enter_break(self):
        self.focus_app.rest()

        self.total_focused_time_label.text = f"🎯 Total focused time: {duration_from_seconds(self.focus_app.get_total_focused_seconds())}"
        self.earned_break_time_label.text = (
            f"⏰ Earned break time: {self.focus_app.earned_break_time // 60} minutes"
        )
        self.total_break_time_label.text = f"☕ Total break time: {duration_from_seconds(self.focus_app.get_total_rested_seconds())}"

        # Update visual state for break mode
        self.start_button.text = "🎯 Focus!"
        self.start_button.style.background_color = "#28a745"
        self.state_indicator.text = "☕ On Break"
        self.state_indicator.style.color = "#007bff"
        self.timer_label.style.color = "#007bff"
        self.cancel_button.style.visibility = "hidden"

    async def _update_timers(self):
        """Updates the timer labels every second."""
        while True:
            if self.focus_app.paused:
                await asyncio.sleep(1)
                continue

            duration = duration_from_seconds(self.focus_app.get_current_clock_time())
            current_break_time = 0
            if self.focus_app.focusing:
                if not self.focus_app.paused:
                    self.timer_label.style.color = "#28a745"
                self.earned_break_time_label.text = f"⏰ Earned break time: {(self.focus_app.earned_break_time + self.focus_app.get_current_clock_time() // self.focus_app.focus_break_ratio) // 60} minutes"
                self.timer_label.text = str(duration)
                self.total_focused_time_label.text = f"🎯 Total focused time: {duration_from_seconds(self.focus_app.get_total_focused_seconds())}"

                # Hide progress bar during focus (not relevant for flexible focusing)
                self.progress_label.text = "Focusing... ⏱️"
                self.break_progress.value = 0.0
            else:
                current_break_time += self.focus_app.get_current_clock_time()
                if not self.focus_app.paused:
                    self.timer_label.style.color = "#007bff"
                self.earned_break_time_label.text = f"⏰ Earned break time: {(self.focus_app.earned_break_time - self.focus_app.get_current_clock_time()) // 60} minutes"
                self.timer_label.text = str(duration)
                self.total_break_time_label.text = f"☕ Total break time: {duration_from_seconds(self.focus_app.get_total_rested_seconds())}"

                # Show break time usage progress
                self.progress_label.text = "Break time used"
                if self.focus_app.earned_break_time > 0:
                    break_progress = min(
                        current_break_time / max(self.focus_app.earned_break_time, 1),
                        1.0,
                    )
                    self.break_progress.value = break_progress
                else:
                    self.break_progress.value = 0.0

            if (self.focus_app.earned_break_time - current_break_time) < 0:
                if self.focus_app.resting and not self.focus_app.paused:
                    self.timer_label.style.color = "#dc3545"  # Red for overtime
                    self.state_indicator.text = "⚠️ Overtime!"
                    self.state_indicator.style.color = "#dc3545"
                    if not self.notified and platform.system() == "Linux":
                        self.notified = True
                        os.system(
                            '/usr/bin/notify-send -t 2000 "Run out of break time"'
                        )
                self.total_break_time_label.style.color = "#dc3545"
            else:
                if self.focus_app.resting and not self.focus_app.paused:
                    self.timer_label.style.color = "#007bff"
                    self.state_indicator.text = "☕ On Break"
                    self.state_indicator.style.color = "#007bff"
                self.total_break_time_label.style.color = "#007bff"

            # Update Cancel button visibility - only show when actively focusing (not paused)
            if self.focus_app.focusing and not self.focus_app.paused:
                self.cancel_button.style.visibility = "visible"
            else:
                self.cancel_button.style.visibility = "hidden"

            await asyncio.sleep(1)

    def _refresh_recent_skills(self):
        """Refresh the recent skills buttons."""
        if hasattr(self, 'recent_box'):
            self.recent_box.clear()
            recent_skills = SkillsService().get_recent_skills(8)
            if not recent_skills:
                # Fallback: show first 8 skills if no usage tracking yet
                all_skills = list(self.focus_app.new_skills.values())
                recent_skills = all_skills[:8]
            
            # Split skills into rows of 4 and rebuild grid
            for row_start in range(0, min(len(recent_skills), 8), 4):
                row_skills = recent_skills[row_start:row_start + 4]
                row_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding=(2, 0)))
                
                for skill in row_skills:
                    btn = toga.Button(
                        skill.name.title()[:8],
                        on_press=lambda w, s=skill.name: self.select_recent_skill(s),
                        style=Pack(
                            padding=(2, 5), 
                            font_size=11,
                            background_color="#e9ecef",
                            color="#495057"
                        ),
                    )
                    row_box.add(btn)
                
                self.recent_box.add(row_box)


def main():
    return FocusApp("Focus!", "org.beeware.tutorial")


if __name__ == "__main__":
    main().main_loop()
