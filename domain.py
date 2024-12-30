from sqlmodel import SQLModel, Field, Relationship
from enums import Difficulty
from typing import Callable
from pydantic import PrivateAttr


class Goal(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    difficulty: Difficulty = Difficulty.EASY
    completed: bool = False

    skill_id: int | None = Field(default=None, foreign_key="skill.id")
