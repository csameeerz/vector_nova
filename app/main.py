from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.logging import setup_logging
from app.core.rate_limiting import RateLimitingMiddleware
from app.api import auth, documents, query, users
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # TODO: Initialize database connections, cache, etc.
    yield
    # Shutdown
    # TODO: Close database connections, cleanup resources

app = FastAPI(
    title="Vector Nova",
    description="A Knowledge Base Application for intelligent document search and query processing",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitingMiddleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(query.router, prefix="/api/v1/query", tags=["Query"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
