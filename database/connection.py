import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# We use SQLite + aiosqlite as the default fallback so MVP can be tested instantly without a PostgreSQL instance.
# In Production, set DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname in .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./science_agent.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    """Initializes the database and creates all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
