from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Fallback to a local default if DATABASE_URL is not set
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/dbname",
)

# If an async driver was specified (e.g. '+asyncpg'), SQLAlchemy sync engine
# can't use it. Replace the async suffix to use the sync driver from requirements.
sync_db_url = DATABASE_URL.replace("+asyncpg", "")

engine = create_engine(sync_db_url, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()