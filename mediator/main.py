import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mediator.api.routes import router as job_router

# Logging config
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s.%(msecs)03d | %(levelname)-7s | %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI(
    title="Mediator",
    version="1.0.0",
    description="Async background job service with FastAPI, Celery, RabbitMQ and PostgreSQL.",
)

# CORS config (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(job_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    logger.info("Mediator starting up...")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Mediator shutting down...")
