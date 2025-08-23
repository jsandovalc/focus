from datetime import datetime

from conf import PRIORITY_ORDER
from domain import Goal, Skill, Stat
from repositories import (
    GoalsRepository,
    GoalUpdate,
    SkillRepository,
    SkillUpdate,
    StatsRepository,
    StatUpdate,
)


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
        if skill.secondary_stat:
            stats_repo.update_stat(
                update=StatUpdate(
                    id=skill.secondary_stat.id, value=skill.secondary_stat.value
                )
            )

        return repository.get_skill_by_id(skill_id)

    def create_skill(
        self, name: str, main_stat_name: str, secondary_stat_name: str | None
    ) -> Skill:
        skill_repo = SkillRepository()
        stats_repo = StatsRepository(skill_repo.session)

        # Get or create main stat
        main_stat = stats_repo.get_stat_by_name(main_stat_name)
        if not main_stat:
            main_stat = stats_repo.create_stat(Stat(name=main_stat_name))

        secondary_stat = None
        if secondary_stat_name:
            secondary_stat = stats_repo.get_stat_by_name(secondary_stat_name)
            if not secondary_stat:
                secondary_stat = stats_repo.create_stat(Stat(name=secondary_stat_name))

        new_skill = Skill(
            name=name,
            main_stat=main_stat,
            secondary_stat=secondary_stat,
        )
        return skill_repo.create_skill(new_skill)

    def get_recent_skills(self, limit: int = 4) -> list[Skill]:
        """Get most recently used skills."""
        repository = SkillRepository()
        return repository.get_skills_by_recent_usage(limit)

    def mark_skill_as_used(self, skill_id: int) -> None:
        """Update the last_used timestamp when skill is selected."""
        repository = SkillRepository()
        repository.update_skill_last_used(skill_id, datetime.now())


class GoalsService:
    def complete_goal(self, goal_id: int) -> Goal:
        repository = GoalsRepository()
        goal = repository.get_goal_by_id(goal_id)

        goal.complete()

        repository.update_goal(
            GoalUpdate(id=goal.id, completed=goal.completed, main_skill=goal.main_skill)
        )

        return repository.get_goal_by_id(goal_id)

    def get_goals_by_priority(self, completed=False):
        """Get goals sorted by priority (URGENT → HIGH → MEDIUM → LOW)"""
        repository = GoalsRepository()
        goals = [
            goal for goal in repository.get_all_goals() if goal.completed == completed
        ]
        return sorted(goals, key=lambda g: PRIORITY_ORDER.get(g.priority.value, 999))

    def update_goal_priority(self, goal_id: int, new_priority) -> Goal:
        """Update a goal's priority"""
        repository = GoalsRepository()
        goal = repository.get_goal_by_id(goal_id)
        
        goal.priority = new_priority
        
        repository.update_goal(
            GoalUpdate(id=goal.id, priority=new_priority)
        )
        
        return repository.get_goal_by_id(goal_id)
