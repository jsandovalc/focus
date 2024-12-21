from timer import Timer
from history import History
from skills import SkillRepository, SkillUpdate


class Focus:
    """Main Focus class.

    I store non-ui related code to Focus application.

    I have two timers: one for focused time and one for break time.

    :ivar focus_break_ratio: The ratio to use to calculate earned_break_time.
    :ivar current_skill: The skil for the current session.

    """

    def __init__(self, db_name: str = "focus.db"):
        self.focused_timer = Timer()
        self.breaks_timer = Timer()

        self.earned_break_time: int = 0
        self.focus_break_ratio = 3

        self.db_name = db_name
        self.history = History(self.db_name)

        self.skills = {}

        self.skills_repository = SkillRepository(self.db_name)

        int_skill = self.skills_repository.get_skill_by_name("Intelligence")

        if not int_skill:
            int_skill = self.skills_repository.create(name="Intelligence")

        self.skills[int_skill.name] = int_skill

        self.current_skill = int_skill

        # For every `_pomodoro_size` minutes, grant `_base_xp` to `current_skill`
        self._base_xp = 10
        self._pomodoro_size = 25 * 60  # In seconds

        # TODO: Add
        # willpower (focus/discipline)
        # Dexterity (efficiency/speed)
        # Charisma (Communication)
        # Vitality (Energy/Well-being)
        # Perception
        # Alchemy
        # Discipline
        #
        # Others
        # Lore (Knowledger)
        # Artifice (crafting/creation)
        #
        # How to handle skill trees?
        #

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

    def focus(self):
        """I start a focus session."""
        if self.resting:
            self.earned_break_time -= self.get_current_clock_time()
        lapse = self.breaks_timer.stop()

        if lapse:
            self.history.add_entries(lapse)

        lapse = self.focused_timer.start()
        if lapse:
            self.history.add_entries(lapse)

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
                    level=self.current_skill.level
                )
            )

            self.earned_break_time += current_clock_time // self.focus_break_ratio

        lapse = self.focused_timer.stop()
        if lapse:
            self.history.add_entries(lapse)

        lapse = self.breaks_timer.start()
        if lapse:
            self.history.add_entries(lapse)

    def pause(self):
        if self.focusing:
            self.focused_timer.pause()
        elif self.resting:
            self.breaks_timer.pause()

    def unpause(self):
        if self.focused_timer.paused:
            lapse = self.focused_timer.start()
            if lapse:
                self.history.add_entries(lapse)
        elif self.breaks_timer.paused:
            lapse = self.breaks_timer.start()
            if lapse:
                self.history.add_entries(lapse)

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
