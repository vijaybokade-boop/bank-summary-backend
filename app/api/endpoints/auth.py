from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from core.security.jwt_handlers import verify_token, create_access_token
from core.config import settings


router = APIRouter()

class TokenRequest(BaseModel):
    username : str
    password : str

class TokenResponse(BaseModel):
    access_token : str
    token_type : str

@router.post("/auth/token/", response_model=TokenResponse, status_code= 200)
async def get_access_token(request_body:TokenRequest):
    if (
        request_body.username != settings.APP_USERNAME
        or request_body.password != settings.APP_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = await create_access_token(data={"sub": request_body.username})
    return {"access_token": token, "token_type": "bearer"}

