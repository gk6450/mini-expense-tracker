from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=text("timezone('Asia/Kolkata', now())"),
        nullable=False,
    )

    expenses = relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan",
    )
