from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship
from app.db.session import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Business date (explicitly IST)
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=text("timezone('Asia/Kolkata', now())"),
        nullable=False,
    )

    client_id = Column(String(36), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "client_id", name="uq_user_clientid"),
    )

    user = relationship("User", back_populates="expenses")
