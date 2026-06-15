import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# We use SQLite + aiosqlite as the default fallback so MVP can be tested instantly without a PostgreSQL instance.
# In Production, set DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname in the environment.
# Render provides free PostgreSQL instances. The DATABASE_URL from Render uses "postgres://" scheme;
# SQLAlchemy requires "postgresql+asyncpg://" so we normalize it here.
_raw_db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./science_agent.db")

# Render gives "postgres://..." but asyncpg needs "postgresql+asyncpg://..."
if _raw_db_url.startswith("postgres://"):
    _raw_db_url = _raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_db_url.startswith("postgresql://") and "+asyncpg" not in _raw_db_url:
    _raw_db_url = _raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = _raw_db_url
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# PostgreSQL needs pool settings; SQLite does not support connection pooling
if IS_SQLITE:
    engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using (handles Render's idle timeout)
    )

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    """Initializes the database and creates all tables."""
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if IS_SQLITE:
            # Backward-compatible migration for SQLite dev environments only
            try:
                await conn.execute(text("ALTER TABLE query_logs ADD COLUMN conversation_id INTEGER REFERENCES conversations(id)"))
            except Exception:
                pass

