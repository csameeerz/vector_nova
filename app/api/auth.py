from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.config import settings
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedException(detail="Incorrect email or password")
    
    if not user.is_active:
        raise BadRequestException(detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
    }


@router.post("/register")
def register(
    email: str,
    password: str,
    full_name: str,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise BadRequestException(detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True,
        is_admin=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active
    }
