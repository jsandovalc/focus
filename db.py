from sqlmodel import Session, SQLModel, create_engine

sqlite_file_name = "focus.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def _get_session_internal() -> Session:
    return Session(engine, expire_on_commit=False)


def get_session() -> Session:
    return _get_session_internal()
