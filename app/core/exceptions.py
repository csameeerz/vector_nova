from typing import Optional, Dict

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(BaseHTTPException):
    def __init__(self, detail: str = "Bad request", headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class UnauthorizedException(BaseHTTPException):
    def __init__(self, detail: str = "Unauthorized", headers: Optional[Dict[str, str]] = None) -> None:
        default_headers: Dict[str, str] = {"WWW-Authenticate": "Bearer"}
        if headers:
            default_headers.update(headers)
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, default_headers)


class ForbiddenException(BaseHTTPException):
    def __init__(self, detail: str = "Not enough permissions", headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class NotFoundException(BaseHTTPException):
    def __init__(self, detail: str = "Not found", headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class ConflictException(BaseHTTPException):
    def __init__(self, detail: str = "Conflict", headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, headers)


