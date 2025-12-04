from __future__ import annotations

import json
from typing import Generator

from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = "sqlite:///./cases.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, index=True)
    data = Column(Text, nullable=False)


Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_case(case_data: dict) -> str:
    return json.dumps(case_data, ensure_ascii=False, separators=(",", ":"))


def deserialize_case(payload: str) -> dict:
    return json.loads(payload)
