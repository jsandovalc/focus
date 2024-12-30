from sqlmodel import Field, Relationship, SQLModel
from typing import Callable
from enums import Difficulty
from pydantic import PrivateAttr
from domain import Goal
from signals import level_gained, xp_gained

_BASE_XP_TO_NEXT_LEVEL = 100
_POMODORO_BLOCK_SIZE = 25 * 60  # seconds
_BASE_XP = 10
_CAP_XP_AT = 15


class Skill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    level: int = 1
    xp: int = 0
    xp_to_next_level: int = _BASE_XP_TO_NEXT_LEVEL

    goals: list["GoalModel"] = Relationship(back_populates="skill")

    def gain_xp(self, time: int):
        """:param time: Seconds in focused block."""
        self.gain_fixed_xp(
            min(int(_BASE_XP * time // _POMODORO_BLOCK_SIZE), _CAP_XP_AT)
        )

    def gain_fixed_xp(self, xp):
        from skills import SkillRepository, SkillUpdate
        self.xp += xp

        xp_gained.send(self, xp=xp)

        if self.xp >= self.xp_to_next_level:
            self.level += 1
            extra_xp = self.xp - self.xp_to_next_level
            self.xp = 0
            self.xp_to_next_level = _BASE_XP_TO_NEXT_LEVEL * self.level

            SkillRepository().update_skill(
                SkillUpdate(
                    id=self.id,
                    xp=self.xp,
                    xp_to_next_level=self.xp_to_next_level,
                    level=self.level,
                )
            )
            level_gained.send(self, xp=extra_xp)

            self.gain_fixed_xp(extra_xp)


class GoalModel(Goal, table=True):
    skill: Skill | None = Relationship(back_populates="goals")
