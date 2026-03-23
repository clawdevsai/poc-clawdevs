from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_password, get_password_hash, create_access_token
from app.core.config import get_settings
from app.core.database import get_session
from app.models import User
from app.api.deps import get_current_user

router = APIRouter()
settings = get_settings()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User).where(User.username == body.username))
    user = result.first()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
        )

    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=str(current_user.id), username=current_user.username, role=current_user.role)
