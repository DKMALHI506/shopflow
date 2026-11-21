from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 - registers models with SQLAlchemy metadata
from app.routers import customers, health, orders, tickets


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Convenient for a local learning project.
    # Use Alembic migrations before deploying a real application.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Customer support operations API for the ShopFlow demo.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(tickets.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to ShopFlow API",
        "documentation": "/docs",
    }
