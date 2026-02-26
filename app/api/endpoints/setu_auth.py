from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.setu_service import setu_login
from core.config import settings
import jwt
from core.security.auth import get_current_user
from fastapi_limiter.depends import RateLimiter
router = APIRouter()

class LoginRequest(BaseModel):
    """Dynamic login request - client provides all data."""
    clientID: str
    grant_type: str
    secret: str
    # Allow extra fields
    model_config = {"extra": "allow"}


def validate_and_extract_headers(request: Request, payload: Dict) -> Dict:
    extracted_headers = {}
    
    if request:
        headers_to_include = ["content-type", "client"]
        for key, value in request.headers.items():
            key_lower = key.lower()
            if any(key_lower.startswith(h) for h in headers_to_include):
                if not value or not str(value).strip():
                    raise HTTPException(
                        status_code=400,
                        detail=f"Header '{key}' cannot be empty"
                    )
                extracted_headers[key] = value
    
    if "client" not in extracted_headers and "client" in payload:
        client_value = payload.get("client")
        if not client_value or not str(client_value).strip():
            raise HTTPException(
                status_code=400,
                detail="Header 'client' cannot be empty"
            )
        extracted_headers["client"] = client_value
        payload.pop("client")
    
    if "client" not in extracted_headers:
        raise HTTPException(
            status_code=400,
            detail="Missing required header: 'client'"
        )
    
    if "content-type" not in extracted_headers and "Content-Type" not in extracted_headers:
        extracted_headers["Content-Type"] = "application/json"
    else:
        provided_content_type = extracted_headers.get("content-type") or extracted_headers.get("Content-Type")
        if "json" not in provided_content_type.lower():
            raise HTTPException(
                status_code=400,
                detail="Content-Type must be 'application/json'"
            )
    
    return extracted_headers

@router.post("/setu/login", status_code=201, dependencies=[Depends(RateLimiter(times = 5, seconds =60))])
async def login(request_body: LoginRequest, request: Request, current_user: str = Depends(get_current_user)):
    payload = request_body.model_dump()
    extracted_headers = validate_and_extract_headers(request, payload)
    data = setu_login(payload, extracted_headers)
    return {
        "status": True,
        "status_code": 201,
        "data": data,
        "msg": "Token generated Successfully!!"
    }



