from blinker import signal

goal_completed = signal("goal-completed")
level_gained = signal("level-gained")
xp_gained = signal("xp-gained")
goal_added = signal("goal-added")
