import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import SessionLocal
from app.features.activities.router import router as activities_router
from app.features.admin.router import router as admin_router
from app.features.auth.router import router as auth_router
from app.features.auth.service import ensure_env_admin_account
from app.features.budget.router import router as budget_router
from app.features.cities.router import router as cities_router
from app.features.itinerary.router import router as itinerary_router
from app.features.sharing.router import router as sharing_router
from app.features.stops.router import router as stops_router
from app.features.trip_activities.router import (
    router as trip_activities_router,
)
from app.features.trips.router import router as trips_router
from app.features.users.router import router as users_router

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        ensure_env_admin_account(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="GlobeTrotter API",
    version="0.1.0",
    description="GlobeTrotter FastAPI backend service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_base_dir = settings.UPLOAD_DIR.split("/")[0]
os.makedirs(upload_base_dir, exist_ok=True)
app.mount(
    f"/{upload_base_dir}",
    StaticFiles(directory=upload_base_dir),
    name="uploads",
)


@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(cities_router)
app.include_router(activities_router)
app.include_router(itinerary_router)
app.include_router(trips_router)
app.include_router(stops_router)
app.include_router(trip_activities_router)
app.include_router(budget_router)
app.include_router(sharing_router)
app.include_router(admin_router)
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
