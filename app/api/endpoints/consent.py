from fastapi import APIRouter, Header,Depends,  HTTPException, Query, Request
from models.consent import ConsentRequest
from services.setu_service import create_consent, get_consent
from fastapi_limiter.depends import RateLimiter 
# from fastapi.responses import JSONResponse
from typing import Optional
from core.security.auth import get_current_user   # ← add this

router = APIRouter()

@router.post("/consents", status_code=201, dependencies=[Depends(RateLimiter(times = 10, seconds = 60))])
async def create_new_consent(
    request_body: ConsentRequest,
    setu_authorization: str = Header(..., alias="X-Setu-Authorization"),
    x_product_instance_id:str = Header(..., alias = "x-product-instance-id"),
    current_user:str = Depends(get_current_user)
    ):
    if not setu_authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Setu token format. Expected 'Bearer <token>'.")
    
    
    headers = {"Authorization": setu_authorization, "x-product-instance-id": x_product_instance_id}
    data = create_consent(request_body.model_dump(by_alias = True), headers=headers)
    return {
        "status": True, 
        "status_code":201,
        "data": data,
        "msg":"Successfully Consent created!!"
    }


@router.get("/consent/{consent_id}", dependencies=[Depends(RateLimiter(times = 20, seconds = 60))])
async def get_consent_details(consent_id: str,x_product_instance_id: str = Header(..., alias = "x-product-instance-id"),
                              current_user: str = Depends(get_current_user), setu_authorization: str = Header(..., alias="X-Setu-Authorization") ):
    if not setu_authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Setu token format. Expected 'Bearer <token>'.")

    headers = {"Authorization":setu_authorization, "x-product-instance-id":x_product_instance_id }
    data = get_consent(consent_id, False,headers)
    return {
        "status": True, 
        "status_code":200,
        "data": data,
        "msg":"Successfully Consent fetched!!"
    }
