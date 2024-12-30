from sqlmodel import select

from db import get_session
from enums import Difficulty
from models import GoalModel
from domain import Goal


_EXCHANGE = {
    Difficulty.EASY: 5,
    Difficulty.MEDIUM: 50,
    Difficulty.HARD: 200,
    Difficulty.PROJECT: 500,
}


class GoalsRepository:
    def __init__(self, db_path="focus.db"):
        self.db_path = db_path

    def add_goal(self, goal: Goal):
        """The goal must be returned, as, internally, we use an internal
        `GoalModel`.

        The id of `goal` gets updated with the inserted id.

        """
        with get_session() as session:
            goal_model = GoalModel.model_validate(goal)
            session.add(goal_model)
            session.commit()

        goal.id = goal_model.id

    def create_goal(
        self,
        *,
        title: str,
        description: str = "",
        difficulty: Difficulty,
        skill_id: int,
    ) -> Goal:
        """:param skill_id: A relation to a skill."""
        with get_session() as session:
            new_goal = GoalModel(
                title=title,
                description=description,
                difficulty=difficulty,
                skill_id=skill_id,
            )
            session.add(new_goal)
            session.commit()

        return Goal.model_validate(new_goal)

    def create(self, *args, **kwargs) -> Goal:
        return self.create_goal(*args, **kwargs)

    def get_goal_by_id(self, id: int) -> Goal | None:
        with get_session() as session:
            goal = session.exec(select(GoalModel).where(GoalModel.id == id)).first()
            return Goal.model_validate(goal)

    def all_goals(self) -> list[Goal]:
        with get_session() as session:
            return [
                Goal.model_validate(goal)
                for goal in session.exec(
                    select(GoalModel).where(GoalModel.completed == False)
                ).all()
            ]

    def complete_goal(self, goal_id: int) -> Goal:
        with get_session() as session:
            goal = session.exec(
                select(GoalModel).where(GoalModel.id == goal_id)
            ).first()
            goal.completed = True
            goal.skill.gain_fixed_xp(_EXCHANGE[goal.difficulty])
            session.add(goal)
            session.commit()

        return Goal.model_validate(goal)
