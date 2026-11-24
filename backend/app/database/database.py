from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings


DATABASE_URL = settings.DATABASE_URL

# Prevent accidental SQLite usage
if not DATABASE_URL.startswith("postgresql"):
    raise RuntimeError(
        "TruthLens AI requires Neon PostgreSQL. "
        f"Invalid DATABASE_URL: {DATABASE_URL.split('@')[0]}"
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()