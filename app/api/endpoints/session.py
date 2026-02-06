from fastapi import APIRouter, Header, HTTPException, Depends
from models.session import SessionRequest
from services.setu_service import create_session, get_sessions
from fastapi_limiter.depends import RateLimiter

router = APIRouter()


@router.post("/sessions", status_code=201, dependencies=[Depends(RateLimiter(times = 10, seconds =60))])
async def create_new_session(
    request_body: SessionRequest,
    authorization: str = Header(..., description="Setu authorization token"),
    x_product_instance_id: str = Header(
        ..., alias="x-product-instance-id",
        description="Setu product instance ID"
    )
):
    headers = {
        "Authorization": authorization,
        "x-product-instance-id": x_product_instance_id,
        "Content-Type": "application/json"
    }

    data = create_session(request_body.model_dump(by_alias=True), headers)
    return {
        "status": True, 
        "status_code": 201,
        "data": data,
        "msg": "Session created Successfully!!"
    }

@router.get("/sessions/{session_id}", dependencies=[Depends(RateLimiter(times = 20, seconds = 60))])
async def get_session_details(
    session_id: str,
    authorization: str = Header(...),
    x_product_instance_id: str = Header(
        ..., alias="x-product-instance-id")
):
    headers = {
        "Authorization": authorization,
        "x-product-instance-id": x_product_instance_id,
        "Content-Type": "application/json"
    }
    data = get_sessions(session_id, headers)
    return {
       
        "status": True, 
        "status_code": 200,
        "data": data,
        "msg": "Session retrieved Successfully!!"
    }
