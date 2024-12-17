from timer import Timer


class Focus:
    """Main Focus class.

    I store non-ui related code to Focus application.

    I have two timers: one for focused time and one for break time.

    :ivar focus_break_ratio: The ratio to use to calculate earned_break_time.

    """

    def __init__(self):
        self.focused_timer = Timer()
        self.breaks_timer = Timer()

        self.earned_break_time: int = 0
        self.focus_break_ratio = 3

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
        self.breaks_timer.stop()
        self.focused_timer.start()

    def rest(self):
        """I start a break lapse. I also add the earned break time."""
        if self.focusing:
            self.earned_break_time += (
                self.get_current_clock_time() // self.focus_break_ratio
            )

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
        elif self.breaks_timer.paused:
            self.breaks_timer.start()

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
