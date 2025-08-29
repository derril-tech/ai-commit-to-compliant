"""
Custom middleware for request handling, rate limiting, and observability.
"""

import json
import time
import uuid
from typing import Callable, Dict, Any

import redis
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ProblemJSONMiddleware(BaseHTTPMiddleware):
    """Convert HTTP exceptions to Problem+JSON format (RFC 7807)."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            problem = {
                "type": f"https://httpstatuses.com/{exc.status_code}",
                "title": exc.detail,
                "status": exc.status_code,
                "instance": request.url.path,
            }
            
            if hasattr(request.state, "request_id"):
                problem["request_id"] = request.state.request_id
            
            return JSONResponse(
                status_code=exc.status_code,
                content=problem,
                headers={"Content-Type": "application/problem+json"},
            )
        except Exception as exc:
            problem = {
                "type": "https://httpstatuses.com/500",
                "title": "Internal Server Error",
                "status": 500,
                "instance": request.url.path,
                "detail": str(exc) if settings.ENVIRONMENT == "development" else None,
            }
            
            if hasattr(request.state, "request_id"):
                problem["request_id"] = request.state.request_id
            
            return JSONResponse(
                status_code=500,
                content=problem,
                headers={"Content-Type": "application/problem+json"},
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting using Redis sliding window."""
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client or redis.from_url(settings.REDIS_URL)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        window = settings.RATE_LIMIT_WINDOW
        limit = settings.RATE_LIMIT_REQUESTS
        
        try:
            current_time = int(time.time())
            pipeline = self.redis_client.pipeline()
            
            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, current_time - window)
            
            # Count current requests
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(uuid.uuid4()): current_time})
            
            # Set expiry
            pipeline.expire(key, window)
            
            results = pipeline.execute()
            current_requests = results[1]
            
            if current_requests >= limit:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(current_time + window),
                    },
                )
            
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(limit - current_requests - 1)
            response.headers["X-RateLimit-Reset"] = str(current_time + window)
            
            return response
            
        except redis.RedisError:
            # If Redis is down, allow the request but log the error
            return await call_next(request)


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Idempotency support using Idempotency-Key header."""
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client or redis.from_url(settings.REDIS_URL)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only apply to POST, PUT, PATCH methods
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)
        
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)
        
        # Create cache key
        cache_key = f"idempotency:{idempotency_key}:{request.url.path}"
        
        try:
            # Check if we've seen this request before
            cached_response = self.redis_client.get(cache_key)
            if cached_response:
                cached_data = json.loads(cached_response)
                return JSONResponse(
                    status_code=cached_data["status_code"],
                    content=cached_data["content"],
                    headers=cached_data.get("headers", {}),
                )
            
            # Process the request
            response = await call_next(request)
            
            # Cache successful responses (2xx status codes)
            if 200 <= response.status_code < 300:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                cached_data = {
                    "status_code": response.status_code,
                    "content": json.loads(response_body.decode()) if response_body else None,
                    "headers": dict(response.headers),
                }
                
                # Cache for 24 hours
                self.redis_client.setex(cache_key, 86400, json.dumps(cached_data))
                
                # Recreate response with body
                return JSONResponse(
                    status_code=response.status_code,
                    content=cached_data["content"],
                    headers=response.headers,
                )
            
            return response
            
        except redis.RedisError:
            # If Redis is down, process normally
            return await call_next(request)
