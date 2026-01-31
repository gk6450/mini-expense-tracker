from datetime import datetime, timedelta
from typing import Optional
import jwt

from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to hash password",
        ) from exc

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

def create_access_token(
    subject: int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # FIX: Convert subject to string
    payload = {"sub": str(subject), "iat": now, "exp": expire}
    
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")