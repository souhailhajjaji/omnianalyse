from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from app.models.schemas import LoginRequest, Token
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()

FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@omnianalyse.com",
        "password": "admin123",
        "is_active": True
    }
}

@router.post("/login", response_model=Token)
def login(request: LoginRequest):
    user = FAKE_USERS_DB.get(request.username)
    if not user or request.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}