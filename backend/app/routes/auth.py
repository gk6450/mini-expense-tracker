from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.auth import UserCreate, UserRead, Token
from app.crud.auth import create_user, get_user_by_email, authenticate_user
from app.services import auth as auth_svc
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth_svc.hash_password(user_in.password)
    user = await create_user(db, user_in.email, hashed)
    logger.info("Registered user %s", user.email)
    return user

@router.post("/login", response_model=Token)
async def login(form_data: UserCreate, db: AsyncSession = Depends(get_session)):
    user = await authenticate_user(db, form_data.email, form_data.password, auth_svc.verify_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_svc.create_access_token(subject=user.id)
    logger.info("User logged in: %s", user.email)
    return {"access_token": token, "token_type": "bearer"}
