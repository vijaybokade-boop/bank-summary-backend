from fastapi import APIRouter, Header,Depends,  HTTPException, Query, Request
from models.consent import ConsentRequest
from services.setu_service import create_consent, get_consent
from fastapi_limiter.depends import RateLimiter 
# from fastapi.responses import JSONResponse
from typing import Optional

router = APIRouter()



# @router.post("/consents")
# async def create_new_consent(
#     request_body: ConsentRequest,
#     authorization: str = Header(..., description="Setu authorization token"),
#     x_product_instance_id: str = Header(
#         ..., alias="x-product-instance-id",
#         description="Setu product instance ID"
#     )
# ):
#     # import ipdb;ipdb.set_trace()
#     # Header validations
    
#     if not authorization.startswith("Bearer "):
#         print("#########",authorization)
#         return error_response(
#             400,
#             "Authorization header must be in format: 'Bearer <token>'"
#         )

#     if not x_product_instance_id or not x_product_instance_id.strip():
#         print("!!!!!!!!!",x_product_instance_id)
#         return error_response(
#             400,
#             "x-product-instance-id header cannot be empty"
#         )

#     # Prepare headers for Setu API
#     headers = {
#         "Authorization": authorization,
#         "x-product-instance-id": x_product_instance_id,
#         "Content-Type": "application/json"
#     }

#     try:
#         # Call service layer
#         result = create_consent(
#             request_body.model_dump(by_alias=True),
#             headers
#         )

#         return result
#     except HTTPException:
#         # Let already-handled HTTP errors pass through
#         raise

#     except Exception as e:
#         return error_response(
#             500,
#             f"Consent creation failed: {str(e)}"
#         )


# @router.get("/consent/{consent_id}")
# async def get_consent_details(
#     consent_id: str,
#     expanded: bool = Query(default=False),
#     authorization: str = Header(...),
#     x_product_instance_id: str = Header(..., alias="x-product-instance-id")
# ):

#     if not consent_id or not consent_id.strip():
#         return error_response(400, "consent_id cannot be empty")

#     if not authorization.startswith("Bearer "):
#         return error_response(
#             400,
#             "Authorization header must be in format: 'Bearer <token>'"
#         )

#     if not x_product_instance_id or not x_product_instance_id.strip():
#         return error_response(
#             400,
#             "x-product-instance-id header cannot be empty"
#         )

#     headers = {
#         "Authorization": authorization,
#         "x-product-instance-id": x_product_instance_id
#     }

#     try:
#         result = get_consent(consent_id, expanded, headers)
#         return result
#     except Exception as e:
#         return error_response(
#             500,
#             f"Failed to fetch consent: {str(e)}"
#         )

@router.post("/consents", status_code=201, dependencies=[Depends(RateLimiter(times = 10, seconds = 60))])
async def create_new_consent(
    request_body: ConsentRequest,
    authorization: str = Header(...),
    x_product_instance_id:str = Header(..., alias = "x-product-instance-id")
    ):

    if not authorization.startswith("Bearer"):
        raise HTTPException(status_code=400, detail = "Invalid token format!!")
    
    headers = {"Authorization": authorization, "x-product-instance-id": x_product_instance_id}
    data = create_consent(request_body.model_dump(by_alias = True), headers=headers)
    return {
        "status": True, 
        "status_code":201,
        "data": data,
        "msg":"Successfully Consent created!!"
    }


@router.get("/consent/{consent_id}", dependencies=[Depends(RateLimiter(times = 20, seconds = 60))])
async def get_consent_details(consent_id: str,x_product_instance_id: str = Header(..., alias = "x-product-instance-id"), authorization: str = Header(...) ):
    headers = {"Authorization":authorization, "x-product-instance-id":x_product_instance_id }
    data = get_consent(consent_id, False,headers)
    return {
        "status": True, 
        "status_code":200,
        "data": data,
        "msg":"Successfully Consent fetched!!"
    }
