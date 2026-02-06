import logging
import requests
from fastapi.encoders import jsonable_encoder
from core.config import settings
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from dateutil import tz
from fastapi import HTTPException

# Setup logging
logger = logging.getLogger(__name__)

def setu_login(payload: dict, headers: dict = None):
    required_fields = ["clientID", "grant_type", "secret"]
    missing_fields = [field 
                      for field in required_fields 
                      if field not in payload or payload[field] is None
                    ]
    
    if missing_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    headers = {
            "client": headers["client"] if headers and "client" in headers else None,
            "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            settings.SETU_LOGIN_URL,
            headers=headers,
            json=payload,
            timeout=10,
        )
        
        if response.status_code >= 400:
            error_data = response.json()
            error_msg = error_data.get("message") or error_data.get("error") or str(error_data)
            raise HTTPException(
                status_code=response.status_code, 
                detail=error_msg
            )
        
        return response.json()
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Setu API timeout (10 seconds)")
        
    except requests.exceptions.ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Setu connection error: {str(e)}")
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Setu request error: {str(e)}")

def create_daterange():
    UTC = tz.tzutc()
    # Always create aware datetime
    to_date = datetime.now(tz=UTC)
    from_date = to_date - relativedelta(months = 24)

    # Normalize to midnight (optional but recommended)
    from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
    to_date = to_date.replace(hour=0, minute=0, second=0, microsecond=0)

    print("today_date", to_date, from_date)

    return from_date, to_date

def payload_daterange_update(payload, from_date, to_date):

    try:
        if payload:
            if "dataRange" in payload:
                if "from" in payload["dataRange"] and "to" in  payload["dataRange"]:
                    payload["dataRange"]["from"] = from_date
                    payload["dataRange"]["to"] = to_date
                    return payload
    except Exception as ex:
        print(ex)

def create_consent(payload: dict, headers: dict):
    try:
        # print("$$$$$$$$$$",payload)
        from_date, to_date = create_daterange() 
        # import ipdb;ipdb.set_trace()
        payload = payload_daterange_update(payload, from_date, to_date)     
        json_payload = jsonable_encoder(payload)

        new_headers = {
            "Authorization": headers["Authorization"],  # must be SETU token
            "Content-Type": "application/json",
            "x-product-instance-id": headers["x-product-instance-id"],
        }
        response = requests.post(
            settings.SETU_CONSENT_URL,
            headers=new_headers,   # ✅ FIXED
            json=json_payload,
            timeout=10,
        )

        # Handle different HTTP status codes
        if response.status_code >= 400:
            error_data = response.json()
            error_msg = error_data.get("message") or error_data.get("error") or str(error_data)
            raise HTTPException(status_code=response.status_code, detail=error_msg)

        # print('API' , settings.SETU_CONSENT_URL )
        # print("response headers:", response.headers)
        # print("response status:", response.status_code)
        # print("response body:", response.text)

        return response.json()

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Setu Consent API timeout")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error in create_consent: {str(e)}")
                
def get_consent(consent_id: str, expanded: bool, headers: dict):
    try:
        url = f"{settings.SETU_CONSENT_URL}/{consent_id}"
        if expanded:
            url = f"{url}?expanded=true"
        
        request_headers = {
            "Authorization": headers["Authorization"],
            "x-product-instance-id": headers["x-product-instance-id"]
        }
        
        response = requests.get(
            url,
            headers=request_headers,
            timeout=10
        )
        
        if response.status_code >= 400:
            error_data = response.json()
            error_msg = error_data.get("message") or error_data.get("error") or str(error_data)
            raise HTTPException(status_code=response.status_code, detail=error_msg)
        
        return response.json()
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Setu API timeout (10 seconds)")
    except requests.exceptions.ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Setu connection error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
def create_session(payload: dict, headers: dict):
    try:
        request_headers = {
            "Authorization": headers["Authorization"],
            "Content-Type": "application/json",
            "x-product-instance-id": headers["x-product-instance-id"],
        }

        from_date, to_date = create_daterange() 
        payload = payload_daterange_update(payload, from_date, to_date)            
        json_payload = jsonable_encoder(payload)

        response = requests.post(
            settings.SETU_SESSION_URL,
            headers=request_headers,
            json=json_payload,
            timeout=10,
        )

        if response.status_code >= 400:
            error_data = response.json()
            error_msg = error_data.get("message") or error_data.get("error") or str(error_data)
            raise HTTPException(status_code=response.status_code, detail=error_msg)

        return response.json()
        
    except requests.exceptions.Timeout as ex:
        raise HTTPException(status_code=504, detail=str(ex))
    except requests.exceptions.ConnectionError as ex:
        raise HTTPException(status_code=503, detail=str(ex))
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
        
def get_sessions(session_id: str, headers: dict):
    try:
        url = f"{settings.SETU_SESSION_URL}/{session_id}"
        request_headers = {
            "Authorization": headers["Authorization"],
            "x-product-instance-id": headers["x-product-instance-id"],
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            url,
            headers=request_headers,
            timeout=10
        )
        
        if response.status_code >= 400:
            error_data = response.json()
            error_msg = error_data.get("message") or error_data.get("error") or str(error_data)
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
        return response.json()
        
    except requests.exceptions.Timeout as ex:
        raise HTTPException(status_code=504, detail=str(ex))
    except requests.exceptions.ConnectionError as ex:
        raise HTTPException(status_code=503, detail=str(ex))
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
        # return {"error": str(e), "status_code": 500}