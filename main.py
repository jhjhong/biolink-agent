import uvicorn
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.health import router as health_router, background_health_check
from database.connection import init_db
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup behavior
    print("Starting up: Initializing database...")
    await init_db()
    print("Starting background health check task...")
    asyncio.create_task(background_health_check())
    yield
    # Shutdown behavior
    print("Shutting down gracefully...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Scientific Research Agent Platform REST API",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS Middleware to allow Next.js frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api")
app.include_router(health_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
