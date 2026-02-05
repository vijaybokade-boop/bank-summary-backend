from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse
from api.endpoints.setu_auth import router as setu_router
from api.endpoints.consent import router as consent_router
from api.endpoints.session import router as session_router
from core.security.ip_middleware import AllowedIPsMiddleware
# from core.security.mtls_middleware import MTLSMiddleware
from core.config import settings
import logging
# Configure logging
logging.basicConfig(level = logging.DEBUG,
                    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")


app = FastAPI()

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
