from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator
from sqlmodel import Field, SQLModel

from enums import Difficulty
from signals import goal_completed, level_gained, xp_gained

_NEXT_LEVEL_REQUIRED_XP_FACTOR = 1.5
_MAIN_STAT_INCREASE = 2
_SECONDARY_STAT_INCREASE = 1


def _to_lower(s: str) -> str:
    return s.lower()


class SkillBase(SQLModel):
    name: Annotated[str, AfterValidator(_to_lower)] = Field(index=True)
    level: int = 1
    xp: int = 0
    xp_to_next_level: int = 100


class Skill(SkillBase):
    id: int | None = None

    main_stat: Stat
    secondary_stat: Stat | None = None

    def add_xp(self, *, xp_earned: int):
        self.xp += xp_earned

        print("calling event for exp gaining", self, xp_earned)
        xp_gained.send(self, xp_earned=xp_earned)

        while self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp -= self.xp_to_next_level
            self.xp_to_next_level = int(
                self.xp_to_next_level * _NEXT_LEVEL_REQUIRED_XP_FACTOR
            )

            # Grant xp to stats.
            self.main_stat.value += _MAIN_STAT_INCREASE

            if self.secondary_stat:
                self.secondary_stat.value += _SECONDARY_STAT_INCREASE

            level_gained.send(self)


class StatBase(SQLModel):
    name: Annotated[str, AfterValidator(_to_lower)] = Field(index=True)
    value: int = 1


class Stat(StatBase):
    id: int | None = None


class GoalBase(SQLModel):
    title: str
    description: str = ""
    difficulty: Difficulty = Difficulty.EASY
    completed: bool = False


_EXCHANGE = {
    Difficulty.EASY: 10,
    Difficulty.MEDIUM: 100,
    Difficulty.HARD: 400,
    Difficulty.PROJECT: 1000,
}


class Goal(GoalBase):
    id: int | None = None

    main_skill: Skill
    secondary_skill: Skill | None = None

    def complete(self):
        self.completed = True

        self.main_skill.add_xp(xp_earned=_EXCHANGE[self.difficulty])

        if self.secondary_skill:
            self.secondary_skill.add_xp(xp_earned=_EXCHANGE[self.difficulty] // 2)

        goal_completed.send(self)
