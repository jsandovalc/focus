from collections.abc import Iterable

from sqlmodel import Session, SQLModel, select

from db import get_session
from domain import Goal, Skill, Stat
from models import GoalModel, SkillModel, StatModel


class StatUpdate(SQLModel):
    id: int
    value: int | None = None


class SkillUpdate(SQLModel):
    id: int
    name: str | None = None
    level: int | None = None
    xp: int | None = None
    xp_to_next_level: int | None = None

    main_stat: StatUpdate | None = None
    secondary_stat: StatUpdate | None = None


class GoalUpdate(SQLModel):
    id: int
    completed: bool | None = None
    main_skill: SkillUpdate | None = None
    secondary_skill: SkillUpdate | None = None


class BaseRepository:
    def __init__(self, session: Session | None = None):
        self.session = session or get_session()


class SkillRepository(BaseRepository):
    def create_skill(self, skill: Skill) -> Skill:
        """Store skill into the database.

        :return: The `Skill` with the id added.

        """
        skill_args = {
            "name": skill.name,
            "main_stat_id": skill.main_stat.id,
            "secondary_stat_id": skill.secondary_stat.id
            if skill.secondary_stat
            else None,
        }

        main_stat = StatsRepository(session=self.session).get_stat_by_name(
            skill.main_stat.name
        )

        if not main_stat:
            main_stat = StatsRepository(session=self.session).create_stat(
                skill.main_stat
            )
            skill_args["main_stat_id"] = main_stat.id

        secondary_stat = None
        if skill.secondary_stat:
            secondary_stat = StatsRepository(session=self.session).get_stat_by_name(
                skill.secondary_stat.name
            )
            if not secondary_stat:
                secondary_stat = StatsRepository(session=self.session).create_stat(
                    skill.secondary_stat
                )
                skill_args["secondary_stat_id"] = secondary_stat.id

        skill_model = SkillModel(**skill_args)

        self.session.add(skill_model)
        self.session.commit()

        skill.id = skill_model.id

        return skill

    def get_skill_by_name(self, name: str) -> Skill | None:
        """Retrieve a skill by name."""
        skill = self.session.exec(
            select(SkillModel).where(SkillModel.name == name.lower())
        ).first()
        if skill:
            return Skill.model_validate(skill)

        return None

    def get_skill_by_id(self, id: int) -> Skill | None:
        skill = self.session.exec(select(SkillModel).where(SkillModel.id == id)).first()

        if skill:
            return Skill.model_validate(skill)

        return None

    def get_all_skills(self) -> Iterable[Skill]:
        """Return all skills."""
        return (
            Skill.model_validate(skill)
            for skill in self.session.exec(select(SkillModel)).all()
        )

    def update_skill(self, *, update: SkillUpdate) -> Skill:
        skill_to_update = self.session.get(SkillModel, update.id)

        ignore = {"main_stat", "secondary_stat"}
        for field, value in update.model_dump(exclude_unset=True).items():
            if field in ignore:
                continue
            setattr(skill_to_update, field, value)

        self.session.add(skill_to_update)
        if update.main_stat is not None:
            StatsRepository(session=self.session).update_stat(
                update=StatUpdate.model_validate(update.main_stat)
            )
        if update.secondary_stat is not None:
            StatsRepository(session=self.session).update_stat(
                update=StatUpdate.model_validate(update.secondary_stat)
            )

        self.session.commit()

        return Skill.model_validate(skill_to_update)


class StatsRepository(BaseRepository):
    def create_stat(self, stat: Stat) -> Stat:
        """Store `stat` into the database.

        :return: The `Stat` with the id.
        """
        stat_model = StatModel.model_validate(stat)
        self.session.add(stat_model)
        self.session.commit()

        stat.id = stat_model.id

        return stat

    def get_stat_by_name(self, name: str) -> Stat | None:
        stat = self.session.exec(
            select(StatModel).where(StatModel.name == name.lower())
        ).first()
        if stat:
            return Stat.model_validate(stat)

        return None

    def get_all_stats(self) -> Iterable[Stat]:
        """Return all stats."""
        return (
            Stat.model_validate(stat)
            for stat in self.session.exec(select(StatModel)).all()
        )

    def update_stat(self, *, update: StatUpdate) -> Stat:
        stat_to_update = self.session.get(StatModel, update.id)

        for field, value in update.model_dump(exclude_unset=True).items():
            setattr(stat_to_update, field, value)

        self.session.add(stat_to_update)
        self.session.commit()

        return Stat.model_validate(stat_to_update)


class GoalsRepository(BaseRepository):
    def create_goal(self, goal: Goal) -> Goal:
        goal_args = {
            "title": goal.title,
            "description": goal.description,
            "difficulty": goal.difficulty,
            "completed": goal.completed,
            "main_skill_id": goal.main_skill.id,
            "secondary_skill_id": goal.secondary_skill.id
            if goal.secondary_skill
            else None,
        }

        main_skill = SkillRepository(session=self.session).get_skill_by_name(
            goal.main_skill.name
        )

        if not main_skill:
            main_skill = SkillRepository(session=self.session).create_skill(
                goal.main_skill
            )
            goal_args["main_skill_id"] = main_skill.id

        secondary_skill = None
        if goal.secondary_skill:
            secondary_skill = SkillRepository(session=self.session).get_skill_by_name(
                goal.secondary_skill.name
            )
            if not secondary_skill:
                secondary_skill = SkillRepository(session=self.session).create_skill(
                    goal.secondary_skill
                )
                goal_args["secondary_skill_id"] = secondary_skill.id

        goal_model = GoalModel(**goal_args)

        self.session.add(goal_model)
        self.session.commit()

        goal.id = goal_model.id

        return goal

    def get_goal_by_id(self, id: int) -> Goal:
        goal_model = self.session.exec(
            select(GoalModel).where(GoalModel.id == id)
        ).first()

        return Goal.model_validate(goal_model)

    def get_all_goals(self) -> Iterable[Goal]:
        return (
            Goal.model_validate(goal)
            for goal in self.session.exec(select(GoalModel)).all()
        )

    def update_goal(self, update: GoalUpdate) -> Goal:
        goal_to_update = self.session.get(GoalModel, update.id)

        ignore = {"main_skill", "secondary_skill"}
        for field, value in update.model_dump(exclude_unset=True).items():
            if field in ignore:
                continue
            setattr(goal_to_update, field, value)

        self.session.add(goal_to_update)
        if update.main_skill is not None:
            SkillRepository(session=self.session).update_skill(
                update=SkillUpdate.model_validate(update.main_skill)
            )
        if update.secondary_skill is not None:
            SkillRepository(session=self.session).update_skill(
                update=SkillUpdate.model_validate(update.secondary_skill)
            )
        self.session.commit()

        return Goal.model_validate(goal_to_update)
