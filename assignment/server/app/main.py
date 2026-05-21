"""
    Author: Happy Banda
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.api.discovery import router as discovery_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    print("Database tables ready")
    yield

app = FastAPI(
    title="Luso8 Lead Discovery Agent",
    description="Vertical slice for Luso8 Cloud - Lead Discovery Agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(discovery_router)

@app.get("/")
def root():
    return {
        "message": "Luso8 Lead Discovery Agent API is running!",
        "docs": "/docs",
        "health": "/api/healthz"
    }