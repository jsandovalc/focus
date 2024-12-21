from dataclasses import dataclass, fields
import sqlite3


_BASE_XP_TO_NEXT_LEVEL = 100
_POMODORO_BLOCK_SIZE = 25 * 60  # seconds
_BASE_XP = 10


@dataclass
class Skill:
    id: int
    name: str
    level: int = 1
    xp: int = 0
    xp_to_next_level: int = _BASE_XP_TO_NEXT_LEVEL

    def gain_xp(self, time: int):
        """Un leveling, extra xp (more thant `xp_to_next_level`) is discarded.

        :param time: Seconds in focused block.

        """
        self.xp += min(int(_BASE_XP * time // _POMODORO_BLOCK_SIZE), 15)
        if self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp = 0
            self.xp_to_next_level = _BASE_XP_TO_NEXT_LEVEL * self.level


@dataclass
class SkillUpdate:
    id: int
    name: str = None
    level: int = None
    xp: int = None
    xp_to_next_level: int = None


class SkillRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path

        self._conn = sqlite3.connect(
            db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self._conn.row_factory = sqlite3.Row

        self._conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        level INTEGER NOT NULL DEFAULT 1,
        xp INTEGER NOT NULL DEFAULT 0,
        xp_to_next_level INTEGER NOT NULL DEFAULT 100
        );
        """)

    def get_skill_by_id(self, id: int) -> Skill | None:
        """:return: None if no skill with `id`"""
        result = self._conn.execute(
            """
            SELECT id, name, level, xp, xp_to_next_level FROM skills WHERE id = ?;
        """,
            (id,),
        )

        row = result.fetchone()

        if row:
            return Skill(**row)
        return None

    def get_skill_by_name(self, name: str) -> Skill | None:
        result = self._conn.execute(
            """
            SELECT id, name, level, xp, xp_to_next_level FROM skills WHERE name = ?;
        """,
            (name,),
        )
        row = result.fetchone()

        if row:
            return Skill(**row)
        return None

    def create(self, name: str) -> Skill:
        with self._conn:
            result = self._conn.execute(
                """
            INSERT INTO skills (name)
            VALUES (?)""",
                (name,),
            )

            skill_id = result.lastrowid

            return self.get_skill_by_id(skill_id)

    def update(self, skill: SkillUpdate) -> Skill:
        with self._conn:
            setters = []
            values = []
            for field in fields(skill):
                if field.name == "id":
                    continue

                value = getattr(skill, field.name)

                if value is not None:
                    setters.append(f"{field.name} = ?")
                    values.append(value)

            values.append(skill.id)

            query = f"""
            UPDATE skills SET {", ".join(setters)} WHERE id = ?
            """
            result = self._conn.execute(query, tuple(values))

            return self.get_skill_by_id(result.lastrowid)
