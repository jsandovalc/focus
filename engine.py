from sqlmodel import SQLModel, create_engine

sqlite_file_name: str | None = None

engine = None


def start_engine():
    global engine, sqlite_url
    engine = create_engine(sqlite_url)
    SQLModel.metadata.create_all(engine)

    return engine


def get_engine(file_name: str):
    global sqlite_file_name, engine, sqlite_url

    if engine:
        return engine

    sqlite_file_name = file_name
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    return start_engine()
