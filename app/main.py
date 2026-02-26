from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse
from api.endpoints.setu_auth import router as setu_router
from api.endpoints.consent import router as consent_router
from api.endpoints.session import router as session_router
from core.security.ip_middleware import AllowedIPsMiddleware
from core.security.idempotency_middleware import IdempotencyMiddleware
# from core.security.mtls_middleware import MTLSMiddleware
from api.endpoints.auth import router as auth_router
from core.config import settings
import logging
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level = logging.DEBUG,
                    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

@asynccontextmanager
async def lifespan(app = FastAPI):
    redis_connection = redis.from_url(
        settings.REDIS_URL,
        encoding = "utf-8",
        decode_responses = True
    )
    await FastAPILimiter.init(redis_connection)
    yield
    FastAPILimiter.close()

app = FastAPI(lifespan = lifespan)

@app.exception_handler(HTTPException)
async def custome_http_excption_handler(request:Request, exc:HTTPException):
    return JSONResponse(
            status_code=exc.status_code, 
            content = {
                "status":False, 
                "status_code":exc.status_code,
                "error":exc.detail
            }
    )                                                                                                                                                                                                                                                                                                                                                                                                                       
     
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(AllowedIPsMiddleware)
app.add_middleware(
    CORSMiddleware, 
    allow_origins = settings.ALLOWED_IPS,
    allow_credentials = True,
    allow_methods = ["GET","POST"],
    allow_headers =   ['*',]
                        #  ["Autherization", "Content-Type"]
)
app.include_router(setu_router, prefix = "/api/v1",tags = ["Setu Integration"] )
app.include_router(consent_router,prefix = "/api/v1", tags =["Consent Integration"])
app.include_router(session_router, prefix = "/api/v1", tags =["session Integration"])
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])   # ← add this

