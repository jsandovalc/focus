from domain import Skill, Goal
from repositories import (
    SkillRepository,
    SkillUpdate,
    StatsRepository,
    StatUpdate,
    GoalsRepository,
    GoalUpdate,
)
from sqlmodel import Session

from db import get_session


class SkillsService:
    def grant_xp(self, xp_granted: int, *, skill_id: int) -> Skill:
        """Grants xp to a skill."""
        repository = SkillRepository()
        stats_repo = StatsRepository(repository.session)
        skill = repository.get_skill_by_id(skill_id)
        skill.add_xp(xp_earned=xp_granted)

        repository.update_skill(
            update=SkillUpdate(
                id=skill_id,
                level=skill.level,
                xp=skill.xp,
                xp_to_next_level=skill.xp_to_next_level,
            )
        )
        stats_repo.update_stat(
            update=StatUpdate(id=skill.main_stat.id, value=skill.main_stat.value)
        )
        stats_repo.update_stat(
            update=StatUpdate(
                id=skill.secondary_stat.id, value=skill.secondary_stat.value
            )
        )

        return repository.get_skill_by_id(skill_id)


class GoalsService:
    def complete_goal(self, goal_id: int) -> Goal:
        repository = GoalsRepository()
        goal = repository.get_goal_by_id(goal_id)

        goal.complete()

        repository.update_goal(
            GoalUpdate(completed=goal.completed, main_skill=goal.main_skill)
        )
