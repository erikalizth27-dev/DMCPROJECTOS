from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@contextmanager
def transactional_session(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Entrega una sesión cuyo commit o rollback queda gobernado por Session.begin."""
    with factory() as session:
        with session.begin():
            yield session
