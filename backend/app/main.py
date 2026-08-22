from fastapi import Depends, FastAPI

from app.api.auth import router as auth_router
from app.core.database import get_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cases import router as cases_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.rights import router as rights_router
from app.api.rti import router as rti_router
from app.api.schemes import router as schemes_router


app = FastAPI(
    title="NyayaSetu AI API",
    description="AI-powered civic and legal empowerment platform",
    version="1.0.0",
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)
app.include_router(
    cases_router,
    prefix="/api/v1",
)

app.include_router(
    chat_router,
    prefix="/api/v1",
)
app.include_router(
    rti_router,
    prefix="/api/v1",
)

app.include_router(
    rights_router,
    prefix="/api/v1",
)

app.include_router(
    schemes_router,
    prefix="/api/v1",
)

app.include_router(
    documents_router,
    prefix="/api/v1",
)


@app.get("/api/v1/health")
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "nyayasetu-api",
        },
        "message": "API is running",
    }


@app.get("/api/v1/health/database")
async def database_health_check(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("SELECT 1")
    )

    value = result.scalar_one()

    return {
        "success": True,
        "data": {
            "database": "connected",
            "result": value,
        },
        "message": "Database connection is working",
    }