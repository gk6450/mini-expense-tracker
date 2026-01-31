from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.services.auth import verify_password as _verify_password

async def create_user(db: AsyncSession, email: str, hashed_password: str) -> User:
    """
    Create and persist a new user.
    """
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    q = select(User).where(User.email == email)
    res = await db.execute(q)
    return res.scalar_one_or_none()

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    q = select(User).where(User.id == user_id)
    res = await db.execute(q)
    return res.scalar_one_or_none()

async def authenticate_user(db: AsyncSession, email: str, password: str, verify_fn=_verify_password) -> Optional[User]:
    """
    Authenticate user by email and plaintext password using provided verify_fn.
    The default verify_fn comes from app.services.auth.verify_password (passlib).
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_fn(password, user.hashed_password):
        return None
    return user
