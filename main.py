"""Focus! - Qt version

Migration from Toga to PySide6.
"""

import sys

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from domain import Goal
from enums import Difficulty, Priority
from focus import Focus
from services import GoalsService, SkillsService
from signals import goal_added, level_gained, rest_time_reset, xp_gained
from timer import duration_from_seconds


class NewSkillDialog(QDialog):
    """Dialog for creating a new skill."""

    def __init__(self, parent, focus_app):
        super().__init__(parent)
        self.focus_app = focus_app
        self.setWindowTitle("Add a new skill")
        self.setFixedSize(400, 350)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Skill name
        name_label = QLabel("Skill name:")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Skill description
        description_label = QLabel("Skill description:")
        layout.addWidget(description_label)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)

        # Main stat
        main_stat_label = QLabel("Main stat:")
        layout.addWidget(main_stat_label)

        self.main_stat_selection = QComboBox()
        self.main_stat_selection.addItems(
            [stat.name.title() for stat in focus_app.stats.values()]
        )
        layout.addWidget(self.main_stat_selection)

        # Secondary stat
        secondary_stat_label = QLabel("Secondary stat:")
        layout.addWidget(secondary_stat_label)

        self.secondary_stat_selection = QComboBox()
        self.secondary_stat_selection.addItems(
            [stat.name.title() for stat in focus_app.stats.values()]
        )
        layout.addWidget(self.secondary_stat_selection)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)


class NewGoalDialog(QDialog):
    """Dialog for creating a new goal."""

    def __init__(self, parent, focus_app):
        super().__init__(parent)
        self.focus_app = focus_app
        self.setWindowTitle("Add a new goal")
        self.setFixedSize(400, 400)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Goal title
        title_label = QLabel("Goal title:")
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        # Goal description
        description_label = QLabel("Goal description:")
        layout.addWidget(description_label)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)

        # Priority
        priority_label = QLabel("Priority:")
        layout.addWidget(priority_label)

        self.priority_selection = QComboBox()
        self.priority_selection.addItems([p.value.title() for p in Priority])
        # Set default to Medium
        self.priority_selection.setCurrentText(Priority.MEDIUM.value.title())
        layout.addWidget(self.priority_selection)

        # Difficulty
        difficulty_label = QLabel("Difficulty:")
        layout.addWidget(difficulty_label)

        self.difficulty_selection = QComboBox()
        self.difficulty_selection.addItems([enum.value for enum in Difficulty])
        layout.addWidget(self.difficulty_selection)

        # Skill
        skill_label = QLabel("Skill:")
        layout.addWidget(skill_label)

        self.skill_selection = QComboBox()
        self.skill_selection.addItems(
            [skill.name for skill in focus_app.new_skills.values()]
        )
        layout.addWidget(self.skill_selection)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)


class LevelUpDialog(QDialog):
    """Dialog shown when a skill levels up."""

    def __init__(self, parent, skill, previous_level, xp_gained):
        super().__init__(parent)
        self.skill = skill
        self.setWindowTitle("Level Up!")
        self.setFixedSize(500, 450)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header with background
        header_container = QWidget()
        header_container.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #667eea, stop:1 #764ba2); "
            "border-radius: 8px; padding: 20px;"
        )
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        header_container.setLayout(header_layout)

        # Header emoji
        emoji_label = QLabel("🎉")
        emoji_label.setStyleSheet("font-size: 32px; background: transparent;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(emoji_label)

        # Level Up text
        level_label = QLabel("LEVEL UP!")
        level_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: white; "
            "background: transparent; letter-spacing: 2px;"
        )
        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(level_label)

        # Skill name
        skill_label = QLabel(f"{skill.name.title()}")
        skill_label.setStyleSheet(
            "font-size: 18px; font-weight: 600; color: #f0f0f0; "
            "background: transparent;"
        )
        skill_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(skill_label)

        # Level progression
        level_progress_label = QLabel(f"Level {previous_level} → Level {skill.level}")
        level_progress_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #ffd700; "
            "background: transparent;"
        )
        level_progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(level_progress_label)

        layout.addWidget(header_container)

        # XP gained badge
        xp_container = QWidget()
        xp_container.setStyleSheet(
            "background-color: #e8f5e9; border-radius: 6px; padding: 12px;"
        )
        xp_layout = QHBoxLayout()
        xp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        xp_container.setLayout(xp_layout)

        xp_icon = QLabel("⭐")
        xp_icon.setStyleSheet("font-size: 18px; background: transparent;")
        xp_layout.addWidget(xp_icon)

        xp_label = QLabel(f"+{xp_gained} XP")
        xp_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2e7d32; "
            "background: transparent;"
        )
        xp_layout.addWidget(xp_label)

        layout.addWidget(xp_container)

        # Stats increased section
        stats_container = QWidget()
        stats_container.setStyleSheet(
            "background-color: #f3e5f5; border-radius: 6px; padding: 15px;"
        )
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(8)
        stats_container.setLayout(stats_layout)

        stats_header = QLabel("Stats Increased")
        stats_header.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #4a148c; "
            "background: transparent;"
        )
        stats_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(stats_header)

        # Main stat with icon
        main_stat_container = QWidget()
        main_stat_container.setStyleSheet("background: transparent;")
        main_stat_layout = QHBoxLayout()
        main_stat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_stat_container.setLayout(main_stat_layout)

        main_stat_icon = QLabel("▲")
        main_stat_icon.setStyleSheet(
            "font-size: 14px; color: #6a1b9a; background: transparent;"
        )
        main_stat_layout.addWidget(main_stat_icon)

        main_stat_label = QLabel(f"{skill.main_stat.name.title()}: +2")
        main_stat_label.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #6a1b9a; "
            "background: transparent;"
        )
        main_stat_layout.addWidget(main_stat_label)

        stats_layout.addWidget(main_stat_container)

        if skill.secondary_stat:
            secondary_stat_container = QWidget()
            secondary_stat_container.setStyleSheet("background: transparent;")
            secondary_stat_layout = QHBoxLayout()
            secondary_stat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            secondary_stat_container.setLayout(secondary_stat_layout)

            secondary_stat_icon = QLabel("▲")
            secondary_stat_icon.setStyleSheet(
                "font-size: 12px; color: #8e24aa; background: transparent;"
            )
            secondary_stat_layout.addWidget(secondary_stat_icon)

            secondary_stat_label = QLabel(f"{skill.secondary_stat.name.title()}: +1")
            secondary_stat_label.setStyleSheet(
                "font-size: 13px; font-weight: 500; color: #8e24aa; "
                "background: transparent;"
            )
            secondary_stat_layout.addWidget(secondary_stat_label)

            stats_layout.addWidget(secondary_stat_container)

        layout.addWidget(stats_container)

        # Progress to next level
        progress_container = QWidget()
        progress_container.setStyleSheet(
            "background-color: #e3f2fd; border-radius: 6px; padding: 15px;"
        )
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)
        progress_container.setLayout(progress_layout)

        progress_header = QLabel("Next Level Progress")
        progress_header.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #0d47a1; "
            "background: transparent;"
        )
        progress_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(progress_header)

        total_xp_for_level = skill.xp + skill.xp_to_next_level
        current_progress = skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0

        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(current_progress * 100))
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(12)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #bbdefb;
            }
            QProgressBar::chunk {
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976d2, stop:1 #42a5f5);
            }
        """)
        progress_layout.addWidget(progress_bar)

        progress_text = QLabel(f"{skill.xp} / {total_xp_for_level} XP")
        progress_text.setStyleSheet(
            "font-size: 12px; color: #1565c0; background: transparent;"
        )
        progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(progress_text)

        layout.addWidget(progress_container)

        # OK button
        ok_button = QPushButton("Awesome!")
        ok_button.setFixedSize(140, 40)
        ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-size: 15px;
                font-weight: bold;
                border: none;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6a3f92);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a5bc4, stop:1 #5d3682);
            }
        """)
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)

        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)

        self.setLayout(layout)


class FocusMainWindow(QMainWindow):
    """Main window for the Focus application."""

    # Qt signals
    level_gained_signal = Signal(object, int, int)  # skill, previous_level, xp_gained
    xp_gained_signal = Signal(object, int)  # skill, xp_earned
    rest_time_reset_signal = Signal()  # no parameters

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus!")
        self.setGeometry(100, 100, 800, 600)

        # Initialize Focus business logic
        self.focus_app = Focus()

        # Setup system tray icon for notifications
        self.tray_icon = QSystemTrayIcon(self)
        # Use a default icon (you can customize this with an app icon later)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
        self.tray_icon.setVisible(True)
        self.tray_icon.setToolTip("Focus! - Productivity Timer")

        # Track if we've notified about overtime
        self.notified = False

        # Connect Blinker signals to Qt signals
        level_gained.connect(self._on_level_gained_blinker)
        xp_gained.connect(self._on_xp_gained_blinker)
        goal_added.connect(self._on_goal_added_blinker)
        rest_time_reset.connect(self._on_rest_time_reset_blinker)

        # Connect Qt signals to handlers
        self.level_gained_signal.connect(self._handle_level_gained)
        self.xp_gained_signal.connect(self._handle_xp_gained)
        self.rest_time_reset_signal.connect(self._handle_rest_time_reset)

        # Create the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create placeholder tabs
        self._create_timer_tab()
        self._create_stats_tab()
        self._create_skills_tab()
        self._create_goals_tab()

        # Setup timer for updating timer display
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_timer_display)
        self.update_timer.start(1000)  # Update every 1 second

    def _on_level_gained_blinker(self, skill, previous_level, xp_gained):
        """Bridge from Blinker signal to Qt signal."""
        self.level_gained_signal.emit(skill, previous_level, xp_gained)

    def _on_xp_gained_blinker(self, skill, xp_earned):
        """Bridge from Blinker signal to Qt signal."""
        self.xp_gained_signal.emit(skill, xp_earned)

    def _on_goal_added_blinker(self, goal):
        """Bridge from Blinker signal - handle directly."""
        # Refresh the entire goals list to maintain priority ordering
        self._refresh_goals_list()

    def _on_rest_time_reset_blinker(self, sender):
        """Bridge from Blinker signal to Qt signal."""
        self.rest_time_reset_signal.emit()

    def _handle_rest_time_reset(self):
        """Handle rest time reset event - update UI immediately."""
        # UI is automatically updated by _update_timer_display() every second,
        # but we can force an immediate update for better UX
        self._update_timer_display()

    def _handle_level_gained(self, skill, previous_level, xp_gained):
        """Handle level gained event - show dialog and update UI."""
        # Show level up dialog
        dialog = LevelUpDialog(self, skill, previous_level, xp_gained)
        dialog.exec()

        # Update skill card in Skills tab
        if skill.name in self.skills:
            skill_data = self.skills[skill.name]
            skill_data["skill_label"].setText(f"{skill.name.title()}: Level {skill.level}")
            skill_data["xp_label"].setText(f"XP: {skill.xp}")
            skill_data["next_level_label"].setText(f"XP to next level: {skill.xp_to_next_level}")
            skill_data["level_badge"].setText(f"LV.{skill.level}")

            # Update progress bar
            total_xp_for_level = skill.xp + skill.xp_to_next_level
            current_progress = (
                skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0
            )
            skill_data["progress_bar"].setValue(int(current_progress * 100))

            # Update colors based on new level
            colors = self._get_level_colors(skill.level)
            skill_data["skill_card"].setStyleSheet(
                f"background-color: {colors['bg']}; border-radius: 5px;"
            )
            skill_data["level_badge"].setStyleSheet(
                f"font-size: 10px; color: white; background-color: {colors['accent']}; "
                f"padding: 2px 6px; border-radius: 3px;"
            )

        # Update stat cards
        self._update_stat_card(skill.main_stat.name, skill.main_stat.value)
        if skill.secondary_stat:
            self._update_stat_card(skill.secondary_stat.name, skill.secondary_stat.value)

    def _handle_xp_gained(self, skill, xp_earned):
        """Handle XP gained event - update skill card."""
        if skill.name in self.skills:
            skill_data = self.skills[skill.name]
            skill_data["xp_label"].setText(f"XP: {skill.xp}")
            skill_data["next_level_label"].setText(f"XP to next level: {skill.xp_to_next_level}")

            # Update progress bar
            total_xp_for_level = skill.xp + skill.xp_to_next_level
            current_progress = (
                skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0
            )
            skill_data["progress_bar"].setValue(int(current_progress * 100))

    def _update_stat_card(self, stat_name, new_value):
        """Update a stat card with a new value."""
        if stat_name not in self.stat_cards:
            return

        stat_data = self.stat_cards[stat_name]
        stat_info = self._get_stat_info(stat_name)
        max_value = stat_info["max"]
        colors = stat_info["colors"]

        # Calculate new progress
        progress = min(new_value / max_value, 1.0) if max_value > 0 else 0

        # Get color scheme based on new value
        if progress >= 0.8:
            color_scheme = colors["high"]
        elif progress >= 0.5:
            color_scheme = colors["medium"]
        else:
            color_scheme = colors["low"]

        # Update widgets
        stat_data["value_label"].setText(str(new_value))
        stat_data["value_label"].setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {color_scheme['accent']};"
        )
        stat_data["progress_bar"].setValue(int(progress * 100))
        stat_data["progress_info"].setText(f"{new_value} / {max_value}")
        stat_data["card_widget"].setStyleSheet(
            f"background-color: {color_scheme['bg']}; border-radius: 5px;"
        )

    def _update_timer_display(self):
        """Update the timer display every second."""
        # Get current time
        current_seconds = self.focus_app.get_current_clock_time()
        duration = duration_from_seconds(current_seconds)
        self.timer_label.setText(str(duration))

        # Update state indicator and button states
        if self.focus_app.focusing:
            # Reset notification flag when focusing (so we can notify again on next break)
            self.notified = False

            self.state_indicator.setText("🎯 Focusing")
            self.state_indicator.setStyleSheet(
                "font-size: 12px; font-weight: 600; color: #28a745; "
                "background: transparent; border: none; letter-spacing: 0.5px;"
            )
            self.start_button.setText("☕ Take Break")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    font-size: 13px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """)
            self.pause_button.setVisible(True)
            self.cancel_button.setVisible(True)

            if self.focus_app.paused:
                self.pause_button.setText("Resume")
                self.state_indicator.setText("⏸ Paused")
                self.state_indicator.setStyleSheet(
                    "font-size: 12px; font-weight: 600; color: #ffc107; "
                    "background: transparent; border: none; letter-spacing: 0.5px;"
                )
            else:
                self.pause_button.setText("Pause")

        elif self.focus_app.resting:
            # Check for overtime and send notification
            earned_break_seconds = self.focus_app.earned_break_time
            current_break_time = self.focus_app.get_current_clock_time()

            if (earned_break_seconds - current_break_time) < 0:
                # We're in overtime!
                self.state_indicator.setText("⚠️ Overtime!")
                self.state_indicator.setStyleSheet(
                    "font-size: 12px; font-weight: 600; color: #dc3545; "
                    "background: transparent; border: none; letter-spacing: 0.5px;"
                )

                # Send notification if we haven't already
                if not self.notified and not self.focus_app.paused:
                    self.notified = True
                    self.tray_icon.showMessage(
                        "Break Time Over!",
                        "Your break time has run out. Time to get back to work!",
                        QSystemTrayIcon.MessageIcon.Warning,
                        3000  # Show for 3 seconds
                    )
                    # Also play system beep for audio feedback
                    QApplication.beep()
            else:
                # Normal break time
                self.state_indicator.setText("☕ Resting")
                self.state_indicator.setStyleSheet(
                    "font-size: 12px; font-weight: 600; color: #007bff; "
                    "background: transparent; border: none; letter-spacing: 0.5px;"
                )

            self.start_button.setText("🎯 Start Focus")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    font-size: 13px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            self.pause_button.setVisible(True)
            self.cancel_button.setVisible(False)

            if self.focus_app.paused:
                self.pause_button.setText("Resume")
                self.state_indicator.setText("⏸ Paused")
                self.state_indicator.setStyleSheet(
                    "font-size: 12px; font-weight: 600; color: #ffc107; "
                    "background: transparent; border: none; letter-spacing: 0.5px;"
                )
            else:
                self.pause_button.setText("Pause")

        else:
            # Check if we're paused (but not actively focusing or resting)
            if self.focus_app.paused:
                self.pause_button.setText("Resume")
                self.pause_button.setVisible(True)
                self.state_indicator.setText("⏸ Paused")
                self.state_indicator.setStyleSheet(
                    "font-size: 12px; font-weight: 600; color: #ffc107; "
                    "background: transparent; border: none; letter-spacing: 0.5px;"
                )
            else:
                self.state_indicator.setText("Ready to Focus")
                self.state_indicator.setStyleSheet(
                    "font-size: 12px; font-weight: 600; color: #6c757d; "
                    "background: transparent; border: none; letter-spacing: 0.5px;"
                )
                self.pause_button.setVisible(False)

            self.start_button.setText("🎯 Start Focus")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    font-size: 13px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            self.cancel_button.setVisible(False)

        # Update break time progress bar
        earned_break_seconds = self.focus_app.earned_break_time

        # If we're resting, show remaining break time (earned - used)
        if self.focus_app.resting:
            current_break_time = self.focus_app.get_current_clock_time()
            remaining_break_seconds = earned_break_seconds - current_break_time

            if remaining_break_seconds > 0 and earned_break_seconds > 0:
                # Still have break time left - show remaining as percentage of earned
                progress_pct = (remaining_break_seconds / earned_break_seconds) * 100
                self.break_progress.setValue(int(progress_pct))
                self.progress_label.setText("Break time remaining")
                self.progress_label.setStyleSheet("font-size: 11px; color: #007bff; background: transparent; border: none;")
            else:
                # Overtime - no break time left
                self.break_progress.setValue(0)
                self.progress_label.setText("⚠️ Overtime!")
                self.progress_label.setStyleSheet("font-size: 11px; color: #dc3545; background: transparent; border: none;")
        else:
            # Not resting - show earned break time available
            if earned_break_seconds > 0:
                # Calculate percentage (assume max break time is 1 hour for visual purposes)
                max_break_seconds = 3600  # 1 hour
                progress_pct = min((earned_break_seconds / max_break_seconds) * 100, 100)
                self.break_progress.setValue(int(progress_pct))
                self.progress_label.setText("Break time available")
                self.progress_label.setStyleSheet("font-size: 11px; color: #28a745; background: transparent; border: none;")
            elif earned_break_seconds < 0:
                # This shouldn't happen when not resting, but handle it anyway
                self.break_progress.setValue(0)
                self.progress_label.setText("No break time")
                self.progress_label.setStyleSheet("font-size: 11px; color: #868e96; background: transparent; border: none;")
            else:
                self.break_progress.setValue(0)
                self.progress_label.setText("Break time progress")
                self.progress_label.setStyleSheet("font-size: 11px; color: #868e96; background: transparent; border: none;")

        # Update session statistics
        total_focused = self.focus_app.get_total_focused_seconds()
        total_break = self.focus_app.get_total_rested_seconds()

        focused_duration = duration_from_seconds(total_focused)
        break_duration = duration_from_seconds(total_break)

        self.total_focused_time_label.setText(str(focused_duration))
        self.total_break_time_label.setText(str(break_duration))

        # Update earned break time label
        if self.focus_app.resting:
            # Show remaining time when resting
            current_break_time = self.focus_app.get_current_clock_time()
            remaining_break_seconds = earned_break_seconds - current_break_time
            remaining_minutes = remaining_break_seconds // 60

            if remaining_break_seconds < 0:
                self.earned_break_time_label.setText(f"-{-remaining_minutes} min")
                self.earned_break_time_label.setStyleSheet(
                    "font-size: 16px; font-weight: 700; color: #dc3545; "
                    "background: transparent; border: none; font-family: monospace;"
                )
            else:
                self.earned_break_time_label.setText(f"{remaining_minutes} min")
                self.earned_break_time_label.setStyleSheet(
                    "font-size: 16px; font-weight: 700; color: #007bff; "
                    "background: transparent; border: none; font-family: monospace;"
                )
        else:
            # Show earned time when not resting (idle or focusing)
            # If focusing, proactively show what will be earned
            if self.focus_app.focusing:
                # Proactive calculation: current earned + what's being earned now
                current_focus_time = self.focus_app.get_current_clock_time()
                projected_earned = earned_break_seconds + (current_focus_time // self.focus_app.focus_break_ratio)
                earned_minutes = projected_earned // 60
            else:
                # Not focusing, just show current earned amount
                earned_minutes = earned_break_seconds // 60

            if earned_break_seconds < 0 or (self.focus_app.focusing and earned_minutes < 0):
                self.earned_break_time_label.setText(f"-{-earned_minutes} min")
                self.earned_break_time_label.setStyleSheet(
                    "font-size: 16px; font-weight: 700; color: #dc3545; "
                    "background: transparent; border: none; font-family: monospace;"
                )
            else:
                self.earned_break_time_label.setText(f"{earned_minutes} min")
                self.earned_break_time_label.setStyleSheet(
                    "font-size: 16px; font-weight: 700; color: #6c757d; "
                    "background: transparent; border: none; font-family: monospace;"
                )

        # Update reset button visibility
        # Show button only when:
        # 1. There's earned break time (> 0)
        # 2. Not currently resting (prevents mid-session reset)
        # 3. Not paused during rest (also a resting state)
        should_show_reset = (
            self.focus_app.earned_break_time > 0
            and not self.focus_app.resting
        )
        self.reset_rest_button.setVisible(should_show_reset)

    def _create_timer_tab(self):
        """Create the Timer tab with all timer controls."""
        # Main container
        timer_container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area for timer content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Content widget inside scroll area
        content_widget = QWidget()
        self.timer_layout = QVBoxLayout()
        self.timer_layout.setContentsMargins(10, 10, 10, 10)
        self.timer_layout.setSpacing(10)
        content_widget.setLayout(self.timer_layout)

        scroll_area.setWidget(content_widget)
        container_layout.addWidget(scroll_area)
        timer_container.setLayout(container_layout)

        # Create timer display card
        self._create_timer_display_card()

        self.tabs.addTab(timer_container, "Timer")

    def _create_timer_display_card(self):
        """Create the main timer display card."""
        # Single unified card
        main_card = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_card.setLayout(main_layout)
        main_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)

        # Timer section
        timer_section = QWidget()
        timer_section.setStyleSheet("background: transparent; border: none;")
        timer_layout = QVBoxLayout()
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(8)
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_section.setLayout(timer_layout)

        # State indicator
        self.state_indicator = QLabel("Ready to Focus")
        self.state_indicator.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #6c757d; "
            "background: transparent; border: none; letter-spacing: 0.5px;"
        )
        self.state_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.state_indicator)

        # Timer display
        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet(
            "font-size: 56px; font-weight: 700; color: #212529; "
            "background: transparent; border: none; font-family: monospace;"
        )
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.timer_label)

        # Progress section with label and bar
        progress_section = QWidget()
        progress_section.setStyleSheet("background: transparent; border: none;")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(4)
        progress_section.setLayout(progress_layout)

        self.progress_label = QLabel("Break time progress")
        self.progress_label.setStyleSheet(
            "font-size: 11px; color: #868e96; background: transparent; border: none;"
        )
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_label)

        self.break_progress = QProgressBar()
        self.break_progress.setMaximum(100)
        self.break_progress.setValue(0)
        self.break_progress.setTextVisible(False)
        self.break_progress.setFixedHeight(8)
        self.break_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #e9ecef;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background-color: #28a745;
            }
        """)
        progress_layout.addWidget(self.break_progress)

        timer_layout.addWidget(progress_section)
        main_layout.addWidget(timer_section)

        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #e9ecef; border: none;")
        main_layout.addWidget(divider)

        # Control buttons
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_container.setLayout(button_layout)

        # Pause button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setFixedSize(90, 36)
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #fff3cd;
                color: #856404;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid #ffc107;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #ffe69c;
            }
            QPushButton:pressed {
                background-color: #ffc107;
            }
        """)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        button_layout.addWidget(self.pause_button)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(90, 36)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f8d7da;
                color: #721c24;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid #dc3545;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #f1aeb5;
            }
            QPushButton:pressed {
                background-color: #dc3545;
                color: white;
            }
        """)
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        # Start/Break button (primary action)
        self.start_button = QPushButton("🎯 Start Focus")
        self.start_button.setFixedSize(130, 36)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.start_button.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(self.start_button)

        main_layout.addWidget(button_container)

        # Divider
        divider2 = QWidget()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet("background-color: #e9ecef; border: none;")
        main_layout.addWidget(divider2)

        # Quick Access buttons section
        quick_access_section = QWidget()
        quick_access_section.setStyleSheet("background: transparent; border: none;")
        quick_access_layout = QVBoxLayout()
        quick_access_layout.setContentsMargins(0, 10, 0, 10)
        quick_access_layout.setSpacing(8)
        quick_access_section.setLayout(quick_access_layout)

        # Quick Access label
        quick_access_label = QLabel("Quick Access:")
        quick_access_label.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #6c757d; "
            "background: transparent; border: none;"
        )
        quick_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quick_access_layout.addWidget(quick_access_label)

        # Grid container for buttons (2 rows x 4 columns)
        self.quick_access_grid = QWidget()
        self.quick_access_grid_layout = QGridLayout()
        self.quick_access_grid_layout.setSpacing(6)
        self.quick_access_grid_layout.setContentsMargins(10, 0, 10, 0)
        self.quick_access_grid.setLayout(self.quick_access_grid_layout)

        # Populate initial buttons
        self._refresh_quick_access_buttons()

        quick_access_layout.addWidget(self.quick_access_grid)
        main_layout.addWidget(quick_access_section)

        # Skill selection
        skill_section = QWidget()
        skill_section.setStyleSheet("background: transparent; border: none;")
        skill_layout = QHBoxLayout()
        skill_layout.setContentsMargins(0, 0, 0, 0)
        skill_layout.setSpacing(10)
        skill_section.setLayout(skill_layout)

        skill_label = QLabel("Current Skill:")
        skill_label.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #495057; "
            "background: transparent; border: none;"
        )
        skill_layout.addWidget(skill_label)

        self.skill_selection = QComboBox()
        skills = [skill.name.title() for skill in self.focus_app.new_skills.values()]
        self.skill_selection.addItems(skills)
        self.skill_selection.setStyleSheet("""
            QComboBox {
                font-size: 13px;
                padding: 6px 10px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                color: #495057;
            }
            QComboBox:hover {
                border-color: #80bdff;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        if skills:
            self.skill_selection.setCurrentText(skills[0])
        self.skill_selection.currentTextChanged.connect(self._on_skill_changed)
        skill_layout.addWidget(self.skill_selection, 1)

        main_layout.addWidget(skill_section)

        # Session statistics
        stats_section = QWidget()
        stats_section.setStyleSheet("background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px;")
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(15, 12, 15, 12)
        stats_layout.setSpacing(20)
        stats_section.setLayout(stats_layout)

        # Focused time
        focused_widget = self._create_stat_widget("Focused", "00:00", "#28a745")
        stats_layout.addWidget(focused_widget)

        # Vertical separator
        sep1 = QWidget()
        sep1.setFixedWidth(1)
        sep1.setStyleSheet("background-color: #dee2e6; border: none;")
        stats_layout.addWidget(sep1)

        # Break time
        break_widget = self._create_stat_widget("Break", "00:00", "#007bff")
        stats_layout.addWidget(break_widget)

        # Vertical separator
        sep2 = QWidget()
        sep2.setFixedWidth(1)
        sep2.setStyleSheet("background-color: #dee2e6; border: none;")
        stats_layout.addWidget(sep2)

        # Earned time (with reset button)
        earned_widget = self._create_earned_time_widget_with_reset()
        stats_layout.addWidget(earned_widget)

        main_layout.addWidget(stats_section)

        self.timer_layout.addWidget(main_card)

    def _create_stat_widget(self, label, value, color):
        """Create a stat display widget."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)

        title = QLabel(label)
        title.setStyleSheet(
            f"font-size: 11px; color: #6c757d; font-weight: 600; "
            f"background: transparent; border: none; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {color}; "
            f"background: transparent; border: none; font-family: monospace;"
        )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        # Store references based on label
        if label == "Focused":
            self.total_focused_time_label = value_label
        elif label == "Break":
            self.total_break_time_label = value_label
        elif label == "Earned":
            self.earned_break_time_label = value_label

        return widget

    def _create_earned_time_widget_with_reset(self):
        """Create the earned time stat widget with reset button."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)

        # Title with reset button
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent; border: none;")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.setLayout(title_layout)

        title = QLabel("EARNED")
        title.setStyleSheet(
            "font-size: 11px; color: #6c757d; font-weight: 600; "
            "background: transparent; border: none; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        title_layout.addWidget(title)

        # Reset button (circular arrow icon)
        self.reset_rest_button = QPushButton()
        self.reset_rest_button.setIcon(
            self.style().standardIcon(self.style().StandardPixmap.SP_BrowserReload)
        )
        self.reset_rest_button.setFixedSize(16, 16)
        self.reset_rest_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(108, 117, 125, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(108, 117, 125, 0.3);
            }
        """)
        self.reset_rest_button.setToolTip("Reset rest time to zero")
        self.reset_rest_button.clicked.connect(self._on_reset_rest_time_clicked)
        self.reset_rest_button.setVisible(False)  # Hidden by default
        title_layout.addWidget(self.reset_rest_button)

        layout.addWidget(title_container)

        # Value label
        self.earned_break_time_label = QLabel("0 min")
        self.earned_break_time_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #6c757d; "
            "background: transparent; border: none; font-family: monospace;"
        )
        self.earned_break_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.earned_break_time_label)

        return widget

    def _on_skill_changed(self, skill_name):
        """Handle skill selection change from dropdown."""
        skill_name_lower = skill_name.lower()
        self.focus_app.set_current_skill(skill_name_lower)

        # Mark skill as used and refresh quick access buttons
        skill = self.focus_app.new_skills.get(skill_name_lower)
        if skill:
            SkillsService().mark_skill_as_used(skill.id)
            self._refresh_quick_access_buttons()

        print(f"Skill changed to: {skill_name}")

    def _on_quick_access_clicked(self, skill_name):
        """Handle quick access button click."""
        skill_name_lower = skill_name.lower()

        # Set the current skill
        if self.focus_app.set_current_skill(skill_name_lower):
            # Update the dropdown to reflect the selection
            self.skill_selection.setCurrentText(skill_name.title())

            # Mark skill as used and refresh buttons
            skill = self.focus_app.new_skills.get(skill_name_lower)
            if skill:
                SkillsService().mark_skill_as_used(skill.id)
                self._refresh_quick_access_buttons()

            print(f"Quick access skill selected: {skill_name}")

    def _refresh_quick_access_buttons(self):
        """Refresh the quick access buttons with most recent skills."""
        # Clear existing buttons
        while self.quick_access_grid_layout.count():
            item = self.quick_access_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get recent skills (up to 8)
        recent_skills = SkillsService().get_recent_skills(8)

        # If no recent skills, use first 8 skills as fallback
        if not recent_skills:
            all_skills = list(self.focus_app.new_skills.values())
            recent_skills = all_skills[:8]

        # Create buttons in a 2x4 grid
        for idx, skill in enumerate(recent_skills[:8]):
            row = idx // 4  # 0 or 1 (2 rows)
            col = idx % 4   # 0-3 (4 columns)

            # Truncate long skill names to 14 characters
            button_text = skill.name.title()
            if len(button_text) > 14:
                button_text = button_text[:14] + "…"

            button = QPushButton(button_text)
            button.setFixedSize(110, 32)

            # Add tooltip with full skill name
            button.setToolTip(skill.name.title())

            # Check if this is the currently selected skill
            is_current = (
                hasattr(self.focus_app, 'current_skill') and
                self.focus_app.current_skill and
                skill.name == self.focus_app.current_skill.name
            )

            # Apply different styling for current vs non-current skills
            if is_current:
                button.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #667eea, stop:1 #764ba2);
                        color: white;
                        font-size: 11px;
                        font-weight: 600;
                        border: 1px solid #5568d3;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #5568d3, stop:1 #6a3f92);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4a5bc4, stop:1 #5d3682);
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e9ecef;
                        color: #495057;
                        font-size: 11px;
                        font-weight: 500;
                        border: 1px solid #ced4da;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #dee2e6;
                        border-color: #adb5bd;
                    }
                    QPushButton:pressed {
                        background-color: #ced4da;
                    }
                """)

            # Use lambda with default argument to capture the skill name
            button.clicked.connect(lambda checked, name=skill.name: self._on_quick_access_clicked(name))

            self.quick_access_grid_layout.addWidget(button, row, col)

    def _on_pause_clicked(self):
        """Handle pause button click - pause or resume timer."""
        if self.focus_app.paused:
            self.focus_app.unpause()
        elif self.focus_app.focusing or self.focus_app.resting:
            self.focus_app.pause()

    def _on_cancel_clicked(self):
        """Handle cancel button click - cancel current focus session."""
        if self.focus_app.focusing:
            self.focus_app.cancel()

    def _on_start_clicked(self):
        """Handle start/break button click - toggle between focus and break."""
        if self.focus_app.focusing:
            # Switch to break
            self.focus_app.rest()
        else:
            # Start focusing
            self.focus_app.focus()

    def _on_reset_rest_time_clicked(self):
        """Handle reset rest time button click - show confirmation dialog."""
        earned_minutes = self.focus_app.earned_break_time // 60

        # Safety check: ensure there's actually time to reset
        if self.focus_app.earned_break_time <= 0:
            return

        # Create confirmation dialog
        reply = QMessageBox.question(
            self,
            "Reset Rest Time?",
            f"This will discard {earned_minutes} minute{'s' if earned_minutes != 1 else ''} "
            f"of accumulated rest time.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default to No for safety
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.focus_app.reset_earned_break_time()

            if not success:
                # Should not happen due to button visibility logic, but handle gracefully
                QMessageBox.warning(
                    self,
                    "Cannot Reset",
                    "Rest time cannot be reset while actively resting.",
                    QMessageBox.StandardButton.Ok
                )

    def _create_stats_tab(self):
        """Create the Stats tab with scrollable stat cards."""
        # Initialize stat cards widget reference dict
        self.stat_cards = {}

        # Create main container widget
        stats_container = QWidget()

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create widget to hold stat cards
        stats_widget = QWidget()
        self.stats_layout = QVBoxLayout()
        self.stats_layout.setContentsMargins(15, 15, 15, 15)
        self.stats_layout.setSpacing(8)
        stats_widget.setLayout(self.stats_layout)

        # Set the stats widget as the scroll area's content
        scroll_area.setWidget(stats_widget)

        # Add scroll area to main container
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll_area)
        stats_container.setLayout(container_layout)

        # Generate stat cards for all stats
        for stat in self.focus_app.stats.values():
            stat_card = self._create_stat_card(stat)
            self.stats_layout.addWidget(stat_card)

        # Add stretch at the end to push cards to the top
        self.stats_layout.addStretch()

        # Add tab
        self.tabs.addTab(stats_container, "Stats")

    def _create_skills_tab(self):
        """Create the Skills tab with scrollable skill cards."""
        # Initialize skills widget reference dict
        self.skills = {}

        # Main container
        skills_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # "New Skill" button at the top
        new_skill_button = QPushButton("New skill")
        new_skill_button.setFixedWidth(150)
        new_skill_button.clicked.connect(self._on_new_skill_clicked)

        # Center the button
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(new_skill_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)

        main_layout.addWidget(button_container)

        # Scroll area for skill cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Widget to hold skill cards
        skills_widget = QWidget()
        self.skills_layout = QVBoxLayout()
        self.skills_layout.setContentsMargins(5, 5, 5, 5)
        self.skills_layout.setSpacing(10)
        skills_widget.setLayout(self.skills_layout)

        scroll_area.setWidget(skills_widget)
        main_layout.addWidget(scroll_area)

        # Generate skill cards for all skills
        for skill in self.focus_app.new_skills.values():
            skill_card = self._create_skill_card(skill)
            self.skills_layout.addWidget(skill_card)

        # Add stretch at the end to push cards to the top
        self.skills_layout.addStretch()

        skills_container.setLayout(main_layout)
        self.tabs.addTab(skills_container, "Skills")

    def _on_new_skill_clicked(self):
        """Handle New Skill button click."""
        dialog = NewSkillDialog(self, self.focus_app)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Get values from dialog
            name = dialog.name_input.text()
            main_stat = dialog.main_stat_selection.currentText()
            secondary_stat = dialog.secondary_stat_selection.currentText()

            # Add skill to the app
            self.focus_app.add_skill(name, main_stat, secondary_stat)

            # Add skill card to UI
            new_skill = self.focus_app.new_skills[name]
            skill_card = self._create_skill_card(new_skill)

            # Insert before the stretch at the end
            self.skills_layout.insertWidget(self.skills_layout.count() - 1, skill_card)

            # Update skill dropdown in timer tab
            self.skill_selection.addItem(name.title())

    def _get_level_colors(self, level):
        """Get color scheme based on skill level."""
        if level >= 20:
            return {"bg": "#e8f5e8", "border": "#4CAF50", "accent": "#2E7D32"}  # Green - Master
        elif level >= 15:
            return {"bg": "#fff3e0", "border": "#FF9800", "accent": "#E65100"}  # Orange - Expert
        elif level >= 10:
            return {"bg": "#e3f2fd", "border": "#2196F3", "accent": "#0D47A1"}  # Blue - Advanced
        elif level >= 5:
            return {"bg": "#f3e5f5", "border": "#9C27B0", "accent": "#4A148C"}  # Purple - Intermediate
        else:
            return {"bg": "#f8f9fa", "border": "#9E9E9E", "accent": "#424242"}  # Gray - Beginner

    def _create_skill_card(self, skill):
        """Create a skill card with all elements."""
        # Get color scheme based on level
        colors = self._get_level_colors(skill.level)

        # Main card widget
        card_widget = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(5)

        # Header: Skill name and level badge
        header_layout = QHBoxLayout()

        skill_name_label = QLabel(f"{skill.name.title()}: Level {skill.level}")
        skill_name_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding-bottom: 5px;"
        )

        # Level badge
        level_badge = QLabel(f"LV.{skill.level}")
        level_badge.setStyleSheet(
            f"font-size: 10px; color: white; background-color: {colors['accent']}; "
            f"padding: 2px 6px; border-radius: 3px;"
        )
        level_badge.setFixedHeight(20)

        header_layout.addWidget(skill_name_label)
        header_layout.addStretch()
        header_layout.addWidget(level_badge)

        # XP Progress bar
        total_xp_for_level = skill.xp + skill.xp_to_next_level
        current_progress = (
            skill.xp / total_xp_for_level if total_xp_for_level > 0 else 0
        )

        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(current_progress * 100))
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(8)

        # XP labels
        xp_label = QLabel(f"XP: {skill.xp}")
        xp_label.setStyleSheet("font-size: 12px; color: #666666;")

        next_level_label = QLabel(f"XP to next level: {skill.xp_to_next_level}")
        next_level_label.setStyleSheet("font-size: 12px; color: #666666;")

        # Stats info
        stats_text = f"Main stat: {skill.main_stat.name.title()}"
        if skill.secondary_stat:
            stats_text += f"  Secondary stat: {skill.secondary_stat.name.title()}"

        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-size: 11px; color: #888888; padding-top: 5px;")

        # Add all elements to card
        card_layout.addLayout(header_layout)
        card_layout.addWidget(progress_bar)
        card_layout.addWidget(xp_label)
        card_layout.addWidget(next_level_label)
        card_layout.addWidget(stats_label)

        # Apply styling
        card_widget.setLayout(card_layout)
        card_widget.setStyleSheet(f"background-color: {colors['bg']}; border-radius: 5px;")

        # Store references for updating
        self.skills[skill.name] = {
            "skill_label": skill_name_label,
            "xp_label": xp_label,
            "next_level_label": next_level_label,
            "stats_label": stats_label,
            "progress_bar": progress_bar,
            "level_badge": level_badge,
            "skill_card": card_widget,
        }

        return card_widget

    def _create_goals_tab(self):
        """Create the Goals tab with scrollable goal list."""
        # Main container
        goals_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # "New Goal" button at the top
        new_goal_button = QPushButton("New goal")
        new_goal_button.setFixedWidth(150)
        new_goal_button.clicked.connect(self._on_new_goal_clicked)

        # Center the button
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(new_goal_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)

        main_layout.addWidget(button_container)

        # Scroll area for goal rows
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Widget to hold goal rows
        goals_widget = QWidget()
        self.goals_layout = QVBoxLayout()
        self.goals_layout.setContentsMargins(5, 5, 5, 5)
        self.goals_layout.setSpacing(5)
        goals_widget.setLayout(self.goals_layout)

        scroll_area.setWidget(goals_widget)
        main_layout.addWidget(scroll_area)

        # Generate goal rows for all incomplete goals, sorted by priority
        sorted_goals = GoalsService().get_goals_by_priority(completed=False)
        for goal in sorted_goals:
            goal_row = self._create_goal_row(goal)
            self.goals_layout.addWidget(goal_row)

        # Add stretch at the end to push goals to the top
        self.goals_layout.addStretch()

        goals_container.setLayout(main_layout)
        self.tabs.addTab(goals_container, "Goals")

    def _on_new_goal_clicked(self):
        """Handle New Goal button click."""
        dialog = NewGoalDialog(self, self.focus_app)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Get values from dialog
            title = dialog.title_input.text()
            description = dialog.description_input.toPlainText()
            priority = dialog.priority_selection.currentText()
            difficulty = dialog.difficulty_selection.currentText()
            skill_name = dialog.skill_selection.currentText()

            # Create goal object
            goal = Goal(
                title=title,
                description=description,
                priority=Priority(priority.lower()),
                difficulty=difficulty,
                main_skill=self.focus_app.new_skills[skill_name],
            )

            # Add goal to the app (this will trigger _on_goal_added_blinker which refreshes the list)
            self.focus_app.add_goal(goal)

    def _get_difficulty_color(self, difficulty):
        """Return color code based on difficulty level."""
        colors = {
            "easy": "#28a745",  # Green
            "medium": "#ffc107",  # Yellow
            "hard": "#dc3545",  # Red
        }
        return colors.get(difficulty.lower(), "#6c757d")

    def _create_goal_row(self, goal):
        """Create a goal row with all elements."""
        # Main row widget
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 10, 15, 10)
        row_layout.setSpacing(10)

        # Title section (left, takes more space)
        title_label = QLabel(goal.title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0 5px;")
        row_layout.addWidget(title_label, 3)  # Stretch factor 3

        # Priority dropdown
        priority_combo = QComboBox()
        priority_combo.addItems([p.value.title() for p in Priority])
        priority_combo.setCurrentText(goal.priority.value.title())
        priority_combo.setFixedWidth(100)
        priority_combo.setStyleSheet("font-size: 11px; padding: 2px 5px;")

        # Connect priority change handler
        priority_combo.currentTextChanged.connect(
            lambda text, g=goal: self._on_priority_changed(g, text)
        )

        row_layout.addWidget(priority_combo, 1)  # Stretch factor 1

        # Difficulty section
        difficulty_color = self._get_difficulty_color(goal.difficulty)
        difficulty_label = QLabel(goal.difficulty.title())
        difficulty_label.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {difficulty_color}; padding: 0 5px;"
        )
        row_layout.addWidget(difficulty_label, 1)  # Stretch factor 1

        # Skill section
        skill_label = QLabel(goal.main_skill.name)
        skill_label.setStyleSheet("font-size: 12px; color: #6c757d; padding: 0 5px;")
        row_layout.addWidget(skill_label, 2)  # Stretch factor 2

        # Completion checkbox
        completion_checkbox = QCheckBox("Done")
        completion_checkbox.setChecked(goal.completed)
        completion_checkbox.setEnabled(not goal.completed)
        completion_checkbox.stateChanged.connect(
            lambda state, g=goal, t=title_label, c=completion_checkbox:
            self._on_goal_completed(g, t, c)
        )
        row_layout.addWidget(completion_checkbox, 1)  # Stretch factor 1

        # Apply styling
        row_widget.setLayout(row_layout)
        row_widget.setStyleSheet("background-color: #f8f9fa; border-radius: 3px;")

        return row_widget

    def _on_priority_changed(self, goal, new_priority_text):
        """Handle priority change for a goal."""
        new_priority = Priority(new_priority_text.lower())
        GoalsService().update_goal_priority(goal.id, new_priority)
        # Refresh goals list to maintain priority ordering
        self._refresh_goals_list()

    def _on_goal_completed(self, goal, title_label, checkbox):
        """Handle goal completion."""
        if goal.completed:
            return

        # Mark as completed in database
        self.focus_app.complete_goal(goal.id)

        # Disable the checkbox and title
        checkbox.setEnabled(False)
        title_label.setEnabled(False)

    def _refresh_goals_list(self):
        """Refresh the goals list with updated priorities."""
        # Clear existing goals
        while self.goals_layout.count():
            child = self.goals_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Re-add goals sorted by priority
        sorted_goals = GoalsService().get_goals_by_priority(completed=False)
        for goal in sorted_goals:
            goal_row = self._create_goal_row(goal)
            self.goals_layout.addWidget(goal_row)

        # Add stretch at the end
        self.goals_layout.addStretch()

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

    def _create_stat_card(self, stat):
        """Create an enhanced stat card with progress bars and visual indicators."""
        # Get stat configuration
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

        # Create main card widget
        card_widget = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)

        # Header with icon, name, and value
        header_layout = QHBoxLayout()

        # Icon and name section
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 16px; color: {color_scheme['accent']};")

        name_label = QLabel(stat.name.title())
        name_label.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {color_scheme['text']};"
        )

        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()

        # Value display
        value_label = QLabel(str(stat.value))
        value_label.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {color_scheme['accent']};"
        )
        header_layout.addWidget(value_label)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(progress * 100))
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(8)

        # Progress info text
        progress_info = QLabel(f"{stat.value} / {max_value}")
        progress_info.setStyleSheet(
            f"font-size: 11px; color: {color_scheme['secondary']};"
        )

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(
            f"font-size: 10px; color: {color_scheme['secondary']};"
        )
        desc_label.setWordWrap(True)

        # Add all elements to card layout
        card_layout.addLayout(header_layout)
        card_layout.addWidget(progress_bar)
        card_layout.addWidget(progress_info)
        card_layout.addWidget(desc_label)

        # Apply background color
        card_widget.setLayout(card_layout)
        card_widget.setStyleSheet(f"background-color: {color_scheme['bg']}; border-radius: 5px;")

        # Store widget references for updates
        self.stat_cards[stat.name] = {
            "value_label": value_label,
            "progress_bar": progress_bar,
            "progress_info": progress_info,
            "card_widget": card_widget,
            "stat": stat,
        }

        return card_widget


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = FocusMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
