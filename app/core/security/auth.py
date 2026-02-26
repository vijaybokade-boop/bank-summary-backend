from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.security.jwt_handlers import verify_token


security = HTTPBearer()

async def get_current_user(credentials:HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception =  HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "could not validate credentials",
            headers = {"WWW-Authenticate":"Bearer"}
        )
    token  = credentials.credentials
    username = await verify_token(token, credentials_exception)
    return username



