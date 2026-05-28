import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load variables from .env into the process environment.
load_dotenv()

# Pull the database URL out of the environment.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Did you create a .env file?")

# The engine is the low-level connection pool to Postgres.
# One engine per app — created once and reused.
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory: calling SessionLocal() gives us a new Session.
# A Session is the workspace for talking to the DB (queries, adds, commits).
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base is the parent class every SQLAlchemy model will inherit from.
# It carries the metadata (table definitions) used by create_all().
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a Session per request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
