from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.core.exceptions import UnauthorizedException, BadRequestException, ForbiddenException


security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(detail="Could not validate credentials")
    except JWTError:
        raise UnauthorizedException(detail="Could not validate credentials")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedException(detail="Could not validate credentials")
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise BadRequestException(detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise ForbiddenException(detail="Not enough permissions")
    return current_user
