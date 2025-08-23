import sqlite3

from sqlmodel import Session, SQLModel, create_engine

sqlite_file_name = "focus.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    migrate_database()


def migrate_database():
    """Apply any necessary database migrations."""
    conn = sqlite3.connect(sqlite_file_name)
    cursor = conn.cursor()

    # Check if priority column exists in goalmodel
    cursor.execute("PRAGMA table_info(goalmodel)")
    goal_columns = [column[1] for column in cursor.fetchall()]

    if "priority" not in goal_columns:
        # Add priority column with default value 'MEDIUM' (matches enum)
        cursor.execute(
            "ALTER TABLE goalmodel ADD COLUMN priority TEXT DEFAULT 'MEDIUM'"
        )
        conn.commit()
    else:
        # Fix any existing lowercase values to match enum
        cursor.execute(
            "UPDATE goalmodel SET priority = 'MEDIUM' WHERE priority = 'medium'"
        )
        conn.commit()

    # Check if last_used column exists in skillmodel
    cursor.execute("PRAGMA table_info(skillmodel)")
    skill_columns = [column[1] for column in cursor.fetchall()]

    if "last_used" not in skill_columns:
        # Add last_used column for skill usage tracking
        cursor.execute(
            "ALTER TABLE skillmodel ADD COLUMN last_used DATETIME"
        )
        conn.commit()

    conn.close()


def _get_session_internal() -> Session:
    return Session(engine, expire_on_commit=False)


def get_session() -> Session:
    return _get_session_internal()
