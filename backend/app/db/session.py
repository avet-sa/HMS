from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from backend.app.core.config import settings

# Load environment variables from .env (if present)
load_dotenv()

# Use centralized configuration
DATABASE_URL = settings.DATABASE_URL

# If an async driver was specified (e.g. '+asyncpg'), SQLAlchemy sync engine
# can't use it. Replace the async suffix to use the sync driver from requirements.
sync_db_url = DATABASE_URL.replace("+asyncpg", "")

engine = create_engine(
    sync_db_url,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    future=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()