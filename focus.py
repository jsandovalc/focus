import db
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
from signals import goal_added
from timer import Timer
from services import SkillsService


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
        self.focus_break_ratio = 3

        self._stats_repository = StatsRepository()
        self.stats: dict[str, Stat] = {}
        self.load_stats()

        self._skills_repository = NewSkillRepository()
        self.new_skills: dict[str, Skill] = {}
        self.load_skills()

        skills = list(self.new_skills.values())

        skill = None
        if skills:
            skill = skills[0]

        self.current_skill: Skill | None = skill

        self._goals_repository = GoalsRepository()

        self.goals: dict[int, Goal] = {}
        self.load_goals()

    def load_goals(self):
        for goal in self._goals_repository.get_all_goals():
            self.goals[goal.id] = goal

    def load_skills(self):
        for skill in self._skills_repository.get_all_skills():
            self.new_skills[skill.name] = skill

    def load_stats(self):
        for stat in self._stats_repository.get_all_stats():
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
        new_goal = GoalsRepository().create_goal(goal)

        self.goals[new_goal.id] = new_goal

        goal_added.send(goal)

    def complete_goal(self, goal_id: int) -> bool:
        """`False` means goal was already completed. No callbacks were run."""
        goals_repository = GoalsRepository()
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
                    level=goal.main_skill.level,
                    xp=goal.main_skill.xp,
                    xp_to_next_level=goal.main_skill.xp_to_next_level,
                ),
                secondary_skill=SkillUpdate(
                    id=goal.secondary_skill.id,
                    level=goal.secondary_skill.level,
                    xp=goal.secondary_skill.xp,
                    xp_to_next_level=goal.secondary_skill.xp_to_next_level,
                )
                if goal.secondary_skill
                else None,
            )
        )

        return True

    def focus(self):
        """I start a focus session."""
        if self.resting:
            self.earned_break_time -= self.get_current_clock_time()
        lapse = self.breaks_timer.stop()
        lapse = self.focused_timer.start()

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
        _POMODORO_BLOCK_SIZE = 25 * 60  # seconds
        _BASE_XP = 10
        _CAP_XP_AT = 30

        if self.focusing:
            current_clock_time = self.get_current_clock_time()
            SkillsService().add_xp(
                min(
                    int(_BASE_XP * current_clock_time // _POMODORO_BLOCK_SIZE),
                    _CAP_XP_AT,
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
            lapse = self.focused_timer.start()
            # if lapse:
            #     self.history.add_entries(lapse)
        elif self.breaks_timer.paused:
            lapse = self.breaks_timer.start()
            # if lapse:
            #     self.history.add_entries(lapse)

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
