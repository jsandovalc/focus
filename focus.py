"""Current skills:

Intelligence:

    Reading: Non-fiction books, academic articles, research papers, complex texts.
    Studying: Completing course modules, taking notes, reviewing material, preparing for exams.
    Learning New Concepts: Mastering new ideas in any field.
    Problem Solving: Solving logic puzzles, riddles, brain teasers, mathematical problems.
    Critical Thinking: Analyzing information, evaluating arguments, forming reasoned judgments.
    Researching: Gathering and synthesizing information for projects or personal enrichment.


Willpower:

XP-Earning Actions:

    Completing Pomodoros: Successfully finishing focused work intervals.
    Achieving Focus Goals: Reaching daily or weekly targets for focused time.
    Practicing Mindfulness: Engaging in meditation, mindful breathing, or body scan exercises.
    Resisting Distractions: Actively avoiding or minimizing interruptions during focused work.
    Overcoming Procrastination: Starting and completing tasks despite the urge to delay.
    Maintaining a Consistent Schedule: Sticking to a planned routine.

Dexterity:

XP-Earning Actions:

    Completing Tasks Ahead of Schedule: Finishing tasks earlier than the deadline.
    Improving Processes: Streamlining workflows, finding more efficient ways to work.
    Using Time Management Techniques: Implementing methods like Eisenhower Matrix, timeboxing, or other productivity strategies.
    Effectively Multitasking (Use with Caution): Successfully juggling multiple tasks when appropriate (multitasking can be detrimental to focus if not done strategically).
    Developing Keyboard Shortcuts: Learning and using shortcuts to speed up work in specific applications.


Vitality:
XP-Earning Actions:

    Getting Enough Sleep: Aiming for 7-9 hours of quality sleep per night.
    Exercising: Engaging in physical activity, such as going to the gym, running, or playing sports.
    Healthy Eating: Consuming nutritious meals and snacks.
    Taking Breaks: Stepping away from work to rest and recharge.
    Managing Stress: Practicing relaxation techniques, engaging in hobbies, spending time in nature.
    Mindful Breaks: Taking breaks that involve mindfulness or meditation, rather than just switching to another screen.


## Specialized sklils



"""
from history import History
from skills import SkillRepository, SkillUpdate
from timer import Timer


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
