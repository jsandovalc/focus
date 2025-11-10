import conf
import db
from db import get_session_context
from domain import Goal, Skill, Stat
from repositories import (
    GoalsRepository,
    GoalUpdate,
    SkillUpdate,
    StatsRepository,
)
from repositories import (
    SkillRepository as NewSkillRepository,
)
from services import SkillsService
from signals import goal_added
from timer import Timer


class Focus:
    """Main Focus class.

    I store non-ui related code to Focus application.

    I have two timers: one for focused time and one for break time.

    :ivar focus_break_ratio: The ratio to use to calculate earned_break_time.
    :ivar current_skill: The skil for the current session.

    """

    def __init__(self):
        db.create_db_and_tables()
        self.focused_timer = Timer()
        self.breaks_timer = Timer()

        self.earned_break_time: int = 0
        self.focus_break_ratio = conf.BREAK_RATIO

        self.stats: dict[str, Stat] = {}
        self.load_stats()

        self.new_skills: dict[str, Skill] = {}
        self.load_skills()

        skills = list(self.new_skills.values())

        skill = None
        if skills:
            skill = skills[0]

        self.current_skill: Skill | None = skill

        self.goals: dict[int, Goal] = {}
        self.load_goals()

    def load_goals(self):
        with get_session_context() as session:
            goals_repository = GoalsRepository(session)
            for goal in goals_repository.get_all_goals():
                self.goals[goal.id] = goal

    def load_skills(self):
        with get_session_context() as session:
            skills_repository = NewSkillRepository(session)
            for skill in skills_repository.get_all_skills():
                self.new_skills[skill.name] = skill

    def load_stats(self):
        with get_session_context() as session:
            stats_repository = StatsRepository(session)
            for stat in stats_repository.get_all_stats():
                self.stats[stat.name] = stat

    @property
    def focusing(self) -> bool:
        return self.focused_timer.running

    @property
    def resting(self) -> bool:
        return self.breaks_timer.running

    @property
    def started(self) -> bool:
        return self.focusing or self.resting

    @property
    def paused(self) -> bool:
        return self.focused_timer.paused or self.breaks_timer.paused

    def add_goal(self, goal: Goal):
        with get_session_context() as session:
            new_goal = GoalsRepository(session).create_goal(goal)
            self.goals[new_goal.id] = new_goal
            goal_added.send(goal)

    def add_skill(
        self, name: str, main_stat_name: str, secondary_stat_name: str | None
    ):
        new_skill = SkillsService().create_skill(
            name, main_stat_name, secondary_stat_name
        )
        self.new_skills[new_skill.name] = new_skill

        if not self.current_skill:
            self.current_skill = new_skill

    def complete_goal(self, goal_id: int) -> bool:
        """`False` means goal was already completed. No callbacks were run."""
        with get_session_context() as session:
            goals_repository = GoalsRepository(session)
            goal = goals_repository.get_goal_by_id(goal_id)

            if goal.completed:
                return False

            goal.complete()

            goals_repository.update_goal(
                GoalUpdate(
                    id=goal.id,
                    completed=goal.completed,
                    main_skill=SkillUpdate(
                        id=goal.main_skill.id,
                        name=goal.main_skill.name,
                        level=goal.main_skill.level,
                        xp=goal.main_skill.xp,
                        xp_to_next_level=goal.main_skill.xp_to_next_level,
                        main_stat=goal.main_skill.main_stat,
                        secondary_stat=goal.main_skill.secondary_stat,
                    ),
                    secondary_skill=SkillUpdate(
                        id=goal.secondary_skill.id,
                        name=goal.secondary_skill.name,
                        level=goal.secondary_skill.level,
                        xp=goal.secondary_skill.xp,
                        xp_to_next_level=goal.secondary_skill.xp_to_next_level,
                        main_stat=goal.secondary_skill.main_stat,
                        secondary_stat=goal.secondary_skill.secondary_stat,
                    )
                    if goal.secondary_skill
                    else None,
                )
            )

            return True

    def focus(self):
        """I start a focus session."""
        if self.resting:
            # Get the current break time BEFORE stopping the timer
            current_break_time = self.get_current_clock_time()
            self.breaks_timer.stop()
            # Deduct the used break time from earned break time
            self.earned_break_time -= current_break_time
        else:
            self.breaks_timer.stop()

        # Ensure earned_break_time is not negative and doesn't "reset" to a previous value
        if self.earned_break_time < 0:  # If it went negative, it means it was depleted
            self.earned_break_time = 0
        self.focused_timer.start()

    def set_current_skill(self, name: str) -> bool:
        """:return: True if skill change successfully."""
        if name in self.new_skills:
            self.current_skill = self.new_skills[name]
            return True

        return False

    def rest(self):
        """I start a break lapse. I also add the earned break time.

        Experience must be added to corresponding skill.

        """
        if self.focusing:
            current_clock_time = self.get_current_clock_time()
            SkillsService().grant_xp(
                min(
                    int(conf.BASE_XP * current_clock_time // conf.POMODORO_BLOCK_SIZE),
                    conf.CAP_XP_AT,
                ),
                skill_id=self.current_skill.id,
            )

            self.earned_break_time += current_clock_time // self.focus_break_ratio

        self.focused_timer.stop()
        self.breaks_timer.start()

    def pause(self):
        if self.focusing:
            self.focused_timer.pause()
        elif self.resting:
            self.breaks_timer.pause()

    def unpause(self):
        if self.focused_timer.paused:
            self.focused_timer.start()
            # if lapse:
            #     self.history.add_entries(lapse)
        elif self.breaks_timer.paused:
            self.breaks_timer.start()
            # if lapse:
            #     self.history.add_entries(lapse)

    def cancel(self):
        """Cancel the current focus session without awarding XP or break time."""
        if self.focusing:
            self.focused_timer.stop()
            # Don't award XP or earned break time - just abandon the session

    def get_current_clock_time(self) -> int:
        """I return elapsed time for current working timer."""
        if self.focused_timer.running:
            return self.focused_timer.get_current_elapsed_time()

        if self.breaks_timer.running:
            return self.breaks_timer.get_current_elapsed_time()

        return 0

    def get_total_focused_seconds(self) -> int:
        return self.focused_timer.get_total_elapsed_time()

    def get_total_rested_seconds(self) -> int:
        return self.breaks_timer.get_total_elapsed_time()

    def reset_earned_break_time(self) -> bool:
        """Reset accumulated break time to zero.

        This operation discards all earned rest time, typically used when
        returning from an external break and wanting a fresh start.

        :return: True if reset was performed, False if operation was blocked.

        Note: Reset is only allowed when NOT actively resting to prevent
        state inconsistency. If currently resting, the operation is rejected.
        """
        # Business rule: Cannot reset during an active rest session
        if self.resting:
            return False

        # Reset the earned break time
        self.earned_break_time = 0

        # Emit signal to notify observers
        from signals import rest_time_reset
        rest_time_reset.send()

        return True
