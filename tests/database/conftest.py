from collections.abc import Generator
from dataclasses import dataclass

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.backend.app.database import Base, create_database_engine, get_db
from app.backend.app.main import app
from framework.database.inspector import DatabaseInspector


@dataclass(frozen=True)
class DatabaseContext:
    client: TestClient
    engine: Engine
    sessions: sessionmaker[Session]
    inspector: DatabaseInspector


@pytest.fixture
def database_context(tmp_path) -> Generator[DatabaseContext, None, None]:
    database_path = tmp_path / "phase7-isolated.db"
    engine = create_database_engine(f"sqlite:///{database_path.as_posix()}")
    sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def isolated_session() -> Generator[Session, None, None]:
        session = sessions()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = isolated_session
    with TestClient(app) as client:
        yield DatabaseContext(
            client=client,
            engine=engine,
            sessions=sessions,
            inspector=DatabaseInspector(engine),
        )
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()
