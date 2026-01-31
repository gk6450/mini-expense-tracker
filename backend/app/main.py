import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.logger import logger  # configure_logging already runs on import
from app.routes import auth, expenses
from app.db.session import engine, Base

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers after middleware is configured
app.include_router(auth.router)
app.include_router(expenses.router)

@app.on_event("startup")
async def on_startup():
    logger.info("Starting application, creating DB tables if needed")
    # Create DB tables (not using alembic here by request)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("DB tables ready")
    except Exception as exc:
        # Log error that might have led to 500 responses during early requests
        logger.exception("Error during startup DB initialization: %s", exc)
        raise

@app.get("/")
def root():
    return {"status": "ok", "service": "expense-tracker"}
