from sqlmodel import Field, Relationship, SQLModel
from typing import Callable
from enums import Difficulty
from pydantic import PrivateAttr
from domain import SkillBase, StatBase, GoalBase
from signals import level_gained, xp_gained


class StatModel(StatBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class SkillModel(SkillBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    main_stat_id: int = Field(foreign_key="statmodel.id")
    main_stat: StatModel = Relationship(
        sa_relationship_kwargs=dict(
            foreign_keys="[SkillModel.main_stat_id]",
        )
    )

    secondary_stat_id: int | None = Field(default=None, foreign_key="statmodel.id")
    secondary_stat: StatModel | None = Relationship(
        sa_relationship_kwargs=dict(
            foreign_keys="[SkillModel.secondary_stat_id]",
        ),
    )


class GoalModel(GoalBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    main_skill_id: int = Field(foreign_key="skillmodel.id")
    main_skill: SkillModel = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[GoalModel.main_skill_id]")
    )

    secondary_skill_id: int | None = Field(default=None, foreign_key="skillmodel.id")
    secondary_skill: SkillModel = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[GoalModel.secondary_skill_id]")
    )
