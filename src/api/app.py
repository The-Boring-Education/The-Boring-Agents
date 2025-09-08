"""Main FastAPI application setup."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from . import shiksha_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

# Initialize FastAPI
app = FastAPI(
    title="The Boring Agents API",
    description="API layer exposing agentic systems (Interview, Quiz, Projects, Shiksha, etc.)",
    version="1.0.0",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(shiksha_routes.router)


@app.get("/")
async def root():
    return {"status": True, "message": "Welcome to The Boring Agents API"}
