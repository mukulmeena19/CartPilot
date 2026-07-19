import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logger import setup_logging, get_logger
from app.api.routers import auth, users, categories, products, carts, orders, ai, shopping
from fastapi.middleware.cors import CORSMiddleware

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Ensure DB tables are created
from app.db.base import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Health"])
def root():
    return {"status": "CartPilot API is running", "message": "Visit /docs for the API dashboard."}

# --- MIDDLEWARE ---

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        import structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            client_ip=request.client.host if request.client else None,
            method=request.method,
            path=request.url.path,
        )
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.exception("Unhandled Server Exception", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred."
                    }
                }
            )

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)

# --- EXCEPTION HANDLERS ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": exc.errors()
            }
        },
    )

# --- ROUTERS ---

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(carts.router, prefix=f"{settings.API_V1_STR}/carts", tags=["carts"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["orders"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])
app.include_router(shopping.router, prefix=f"{settings.API_V1_STR}/shopping", tags=["shopping"])

import os
from sqlalchemy import text
from app.db.session import SessionLocal

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

@app.get("/ready", tags=["Health"])
def readiness_check():
    status = {
        "status": "ready",
        "database": "ok",
        "vector_store": "ok",
        "llm_provider": "ok"
    }
    
    # 1. DB Check
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "not_ready"
    finally:
        db.close()
        
    # 2. LLM Provider Check
    provider = os.getenv("LLM_PROVIDER", "openai")
    if provider not in ["openai", "gemini", "mock"]:
        status["llm_provider"] = "error: unknown provider"
        status["status"] = "not_ready"
        
    return status
