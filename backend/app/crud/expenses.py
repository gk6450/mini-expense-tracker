from typing import Optional, List, Tuple
from decimal import Decimal

from sqlalchemy import select, func, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

async def create_expense(
    db: AsyncSession,
    user_id: int,
    expense_in: ExpenseCreate
) -> Expense:
    # Convert provided date to IST
    expense_date = expense_in.date

    if expense_in.client_id:
        q = select(Expense).where(
            Expense.user_id == user_id,
            Expense.client_id == expense_in.client_id,
        )
        res = await db.execute(q)
        existing = res.scalar_one_or_none()
        if existing:
            return existing

    expense = Expense(
        user_id=user_id,
        amount=expense_in.amount,
        category=expense_in.category,
        description=expense_in.description,
        date=expense_date,
        client_id=expense_in.client_id,
    )

    db.add(expense)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        q = select(Expense).where(
            Expense.user_id == user_id,
            Expense.client_id == expense_in.client_id,
        )
        res = await db.execute(q)
        return res.scalar_one()

    await db.commit()
    await db.refresh(expense)
    return expense

async def list_expenses(
    db: AsyncSession,
    user_id: int,
    category: Optional[str] = None,
    sort_date_desc: bool = False,
) -> Tuple[List[Expense], Decimal]:
    q = select(Expense).where(Expense.user_id == user_id)

    if category:
        q = q.where(Expense.category == category)

    q = q.order_by(desc(Expense.date) if sort_date_desc else Expense.date)

    res = await db.execute(q)
    items = res.scalars().all()

    total_q = select(func.coalesce(func.sum(Expense.amount), 0)).where(
        Expense.user_id == user_id
    )
    if category:
        total_q = total_q.where(Expense.category == category)

    total_res = await db.execute(total_q)
    total = Decimal(total_res.scalar_one())

    return items, total

async def get_expense(db: AsyncSession, expense_id: int) -> Optional[Expense]:
    res = await db.execute(select(Expense).where(Expense.id == expense_id))
    return res.scalar_one_or_none()

async def update_expense(
    db: AsyncSession,
    expense: Expense,
    changes: ExpenseUpdate,
) -> Expense:
    updated = False

    if changes.amount is not None:
        expense.amount = changes.amount
        updated = True

    if changes.category is not None:
        expense.category = changes.category
        updated = True

    if changes.description is not None:
        expense.description = changes.description
        updated = True

    if changes.date is not None:
        expense.date = changes.date
        updated = True

    if updated:
        await db.commit()
        await db.refresh(expense)

    return expense

async def delete_expense(db: AsyncSession, expense: Expense) -> None:
    await db.delete(expense)
    await db.commit()
