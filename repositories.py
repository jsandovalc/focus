from domain import Skill, Stat
from sqlmodel import Session, select
from db import get_session
from models import SkillModel, StatModel
from collections.abc import Iterable


class SkillRepository:
    def __init__(self, session: Session | None = None):
        if session is None:
            session = get_session()

        self.session = session

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
            skill_args["main_stat"] = skill.main_stat

        secondary_stat = None
        if skill.secondary_stat:
            secondary_stat = StatsRepository(session=self.session).get_stat_by_name(
                skill.secondary_stat.name
            )
            if not secondary_stat:
                skill_args["secondary_stat"] = skill.secondary_stat

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

    def get_all_skills(self) -> Iterable[Skill]:
        """Return all skills."""
        return (
            Skill.model_validate(skill)
            for skill in self.session.exec(select(SkillModel)).all()
        )


class StatsRepository:
    def __init__(self, session: Session | None = None):
        if session is None:
            session = get_session()

        self.session = session

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
