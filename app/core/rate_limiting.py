from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from app.config import settings

# Simple in-memory rate limiting (use Redis in production)
request_counts = defaultdict(list)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Clean old requests (older than 1 minute)
        current_time = time.time()
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip] 
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(request_counts[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Add current request
        request_counts[client_ip].append(current_time)
        
        # Continue with the request
        response = await call_next(request)
        return response
