from collections.abc import Callable

import db
from goals import Goal, GoalsRepository
from skills import SkillRepository, SkillUpdate
from timer import Timer
from signals import goal_completed
from repositories import SkillRepository as NewSkillRepository, StatsRepository
from domain import Skill, Stat


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

        # self.history = History(self.db_name)

        self.skills = {}

        self.skills_repository = SkillRepository()

        int_skill = self.skills_repository.get_skill_by_name("Intelligence")
        if not int_skill:
            int_skill = self.skills_repository.create(name="Intelligence")

        vit_skill = self.skills_repository.get_skill_by_name("Vitality")
        if not vit_skill:
            vit_skill = self.skills_repository.create(name="Vitality")

        dex_skill = self.skills_repository.get_skill_by_name("Dexterity")
        if not dex_skill:
            dex_skill = self.skills_repository.create(name="Dexterity")

        wil_skill = self.skills_repository.get_skill_by_name("Willpower")
        if not wil_skill:
            wil_skill = self.skills_repository.create(name="Willpower")

        self.skills[int_skill.name] = int_skill
        self.skills[vit_skill.name] = vit_skill
        self.skills[dex_skill.name] = dex_skill
        self.skills[wil_skill.name] = wil_skill

        self.current_skill = int_skill

        self.goals_repository = GoalsRepository()

        self.goals: list[Goal] = self.goals_repository.all_goals()

        self.goal_added_callbacks: list[Callable[[Goal]]] = []

        self._stats_repository = StatsRepository()
        self.stats: dict[str, Stat] = {}
        self.load_stats()

        self._skills_repository = NewSkillRepository()
        self.new_skills: dict[str, Skill] = {}
        self.load_skills()

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
        self.goals.append(goal)

        self.goals_repository.add_goal(goal)

        for callback in self.goal_added_callbacks:
            callback(goal)

    def complete_goal(self, goal_id: int) -> bool:
        """`False` means goal was already completed. No callbacks were run."""
        goal = self.goals_repository.get_goal_by_id(goal_id)

        if goal.completed:
            return False

        goal = self.goals_repository.complete_goal(goal_id)

        goal_completed.send(goal)

        return True

    def focus(self):
        """I start a focus session."""
        if self.resting:
            self.earned_break_time -= self.get_current_clock_time()
        lapse = self.breaks_timer.stop()

        # if lapse:
        #     self.history.add_entries(lapse)

        lapse = self.focused_timer.start()
        # if lapse:
        #     self.history.add_entries(lapse)

    def set_current_skill(self, name: str) -> bool:
        """:return: True if skill change successfully."""
        new_skill = self.skills_repository.get_skill_by_name(name)

        if not new_skill:
            return False

        self.current_skill = new_skill
        return True

    def rest(self):
        """I start a break lapse. I also add the earned break time.

        Experience must be added to corresponding skill.

        """
        if self.focusing:
            current_clock_time = self.get_current_clock_time()
            self.current_skill.gain_xp(current_clock_time)

            self.skills_repository.update(
                SkillUpdate(
                    id=self.current_skill.id,
                    xp=self.current_skill.xp,
                    xp_to_next_level=self.current_skill.xp_to_next_level,
                    level=self.current_skill.level,
                )
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
