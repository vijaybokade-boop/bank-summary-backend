import json
import logging
import asyncio
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from core.config import settings


logger = logging.getLogger(__name__)

class IdempotencyMiddleware(BaseHTTPMiddleware):

    #1.Defined redis_client for global/first time
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
    
    #2.method for get redis client and return it 
    async def get_redis_client(self):
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding = "utf-8",
                decode_responses = True
            )
        return self.redis_client
    
    #3.implement dispatch method
    async def dispatch(self,request:Request, call_next:Callable):
        
        # 1.Only apply idempotency to POST requests
        if request.method != "POST":
            return await call_next(request)
        # 2.Get idempotency key from header
        idempotency_key = request.headers.get("idempotency_key")

        # 3.If no idempotency key, process normally
        if not idempotency_key:
            return await call_next(request)

        # 4.try to get redis_client
        try: 
            redis_client = await self.get_redis_client()
            
            #1. check for cached reposnse and return 
            cache_key = f"idempotency:{idempotency_key}"
            cached_response = await redis_client.get(cache_key)

            if cached_response:
                cached_data = json.loads(cached_response)
                return JSONResponse(
                    status_code=cached_data["status_code"],
                    content = cached_data["body"],
                    headers = {"X-Idempotency-Cached":"true"}
                )
            
            # Check if another request is processing this key
            lock_key = f"{cache_key}:lock_key"
            is_locked = await redis_client.get(lock_key)  
            
            if is_locked:
                cached_response = await self._wait_for_response(
                    redis_client,
                    cache_key,
                    timeout = 30
                )
                if cached_response:
                    cached_data = json.loads(cached_response)
                    
                    return JSONResponse(
                        status_code= cached_data["status_code"],
                        content=cached_data["body"],
                        headers = {"X-Idempotency-Cached":"true"}
                    )
                
            await redis_client.setex(
                lock_key,
                settings.IDEMPOTENCY_LOCK_TTL,
                "processing"
            )    

            response = await call_next(request)
            response_body = b""

            async for chunk in response.body_iterator:
                response_body+=chunk

            try:
                response_data = json.loads(response_body.decode())
            except json.JSONDecodeError:
                response_data=  json.loads(response_body.decode())

            if 200<= response.status_code <300:
                cached_data = {
                        "status_code": response.status_code,
                        "body": response_data,
                        "timestamp":asyncio.get_event_loop().time() 
                }
                await redis_client.setex(
                    cache_key,
                    settings.IDEMPOTENCY_TTL,
                    json.dumps(cached_data)
                )

            await redis_client.delete(lock_key)

            return JSONResponse(
                status_code= response.status_code,
                content=response_data,
                headers = dict(response.headers)
            )
        
        except redis.RedisError as e:
            return await call_next(request)
        except Exception as e:
            return await call_next(request)
    
    async def _wait_for_response(
            self,
            redis_client,cache_key,
            timeout: int=30,
            poll_interval : float  = 0.5
    ):
        elapsed = 0
        while elapsed < timeout:
            cached_response = await redis_client.get(cache_key)
            if cached_response:
                return cached_response
            await asyncio.sleep(poll_interval)
            elapsed+=poll_interval  

        return None
  

 
        





