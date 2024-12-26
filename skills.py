from pydantic import BaseModel
from sqlmodel import select

from db import get_session
from models import Skill


class SkillUpdate(BaseModel):
    id: int
    name: str | None = None
    level: int | None = None
    xp: int | None = None
    xp_to_next_level: int | None = None


class SkillRepository:
    def get_skill_by_id(self, id: int) -> Skill | None:
        """:return: None if no skill with `id`"""
        with get_session() as session:
            return session.exec(select(Skill).where(Skill.id == id)).first()

    def get_skill_by_name(self, name: str) -> Skill | None:
        with get_session() as session:
            return session.exec(select(Skill).where(Skill.name == name)).first()

    def create_skill(self, name: str) -> Skill | None:
        """Create a new skill and tries to retrieve it to return it.

        :return: `None` if couldn't find the created `Skill`.

        """
        with get_session() as session:
            session.add(Skill(name=name))
            session.commit()

        return self.get_skill_by_name(name)

    def create(self, *args, **kwargs) -> Skill | None:
        return self.create_skill(*args, **kwargs)

    def update(self, skill: SkillUpdate) -> Skill:
        with get_session() as session:
            skill_to_update = session.exec(
                select(Skill).where(Skill.id == skill.id)
            ).first()

            for field, value in skill.model_dump(exclude_unset=True).items():
                setattr(skill_to_update, field, value)

            session.add(skill_to_update)
            session.commit()

        return self.get_skill_by_id(skill.id)
