from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from core.config import settings

async def create_access_token(data:dict, expire_delta:Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc)+ expire_delta
    else:
        expire = datetime.now(timezone.utc)+ timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp":expire}) 
    encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY, settings.ALGORITHM)

    return encoded_jwt

async def verify_token(token:str, credentials_exception ):
    try:
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = [settings.ALGORITHM])
        username:str = payload.get("sub")
        if not username:
            raise credentials_exception
        return username
    
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    
