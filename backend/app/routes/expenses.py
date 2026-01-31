from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_session
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseListResponse, ExpenseUpdate
from app.crud.expenses import create_expense, list_expenses, get_expense, update_expense, delete_expense
from app.crud.auth import get_user
from app.utils.logger import logger

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import SECRET_KEY

router = APIRouter(prefix="/expenses", tags=["expenses"])
bearer = HTTPBearer(auto_error=False)

async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: AsyncSession = Depends(get_session)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense_endpoint(expense_in: ExpenseCreate, current_user = Depends(get_current_user_from_token), db: AsyncSession = Depends(get_session)):
    created = await create_expense(db, current_user.id, expense_in)
    logger.info("Expense created for user %s amount=%s", current_user.email, created.amount)
    return created

@router.get("", response_model=ExpenseListResponse)
async def get_expenses(
    category: Optional[str] = Query(None),
    sort: Optional[str] = Query(None, description="use 'date_desc' to sort newest first"),
    current_user = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_session)
):
    sort_date_desc = (sort == "date_desc")
    items, total = await list_expenses(db, current_user.id, category=category, sort_date_desc=sort_date_desc)
    return {"items": items, "total": total, "count": len(items)}

@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense_by_id(expense_id: int = Path(..., gt=0), current_user = Depends(get_current_user_from_token), db: AsyncSession = Depends(get_session)):
    expense = await get_expense(db, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense

@router.put("/{expense_id}", response_model=ExpenseRead)
async def put_update_expense(expense_id: int, changes: ExpenseUpdate, current_user = Depends(get_current_user_from_token), db: AsyncSession = Depends(get_session)):
    expense = await get_expense(db, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    updated = await update_expense(db, expense, changes)
    logger.info("Expense %s updated by user %s", expense_id, current_user.email)
    return updated

@router.patch("/{expense_id}", response_model=ExpenseRead)
async def patch_update_expense(expense_id: int, changes: ExpenseUpdate, current_user = Depends(get_current_user_from_token), db: AsyncSession = Depends(get_session)):
    # Same logic as PUT — partial updates allowed
    expense = await get_expense(db, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    updated = await update_expense(db, expense, changes)
    logger.info("Expense %s patched by user %s", expense_id, current_user.email)
    return updated

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_expense(expense_id: int, current_user = Depends(get_current_user_from_token), db: AsyncSession = Depends(get_session)):
    expense = await get_expense(db, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    await delete_expense(db, expense)
    logger.info("Expense %s deleted by user %s", expense_id, current_user.email)
    return None
