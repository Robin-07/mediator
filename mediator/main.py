from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from mediator.api.endpoints import router as job_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Media Generation API",
    version="1.0.0",
    description="Async background job service with FastAPI, Celery, and PostgreSQL.",
)

# Mount static file serving for local images
app.mount("/media", StaticFiles(directory="media"), name="media")

# CORS config (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(job_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    logger.info("FastAPI app starting up...")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("FastAPI app shutting down...")
