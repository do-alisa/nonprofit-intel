import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/nonprofit",
)

# Allow plain postgresql:// URLs (e.g. from hosting platforms) while
# forcing the psycopg3 driver.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


def get_session():
    with Session(engine) as session:
        yield session