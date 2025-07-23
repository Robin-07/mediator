from fastapi import FastAPI
from mediator.api.endpoints import router
from mediator.core.database import Base, engine

mediator = FastAPI(title="Async Media Generator")

mediator.include_router(router)


@mediator.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
