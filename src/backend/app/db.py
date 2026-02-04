from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite local file. In CI, you can swap to Postgres later.
DATABASE_URL = "sqlite:///./taskmanager.db"

engine = create_engine(
    DATABASE_URL,
    # needed for SQLite + threads
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""Base class for all our models to inherit from."""
class Base(DeclarativeBase):
    pass

"""Return a database session. Closes it after use."""
def get_db() -> sessionmaker:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
