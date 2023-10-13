from datetime import datetime

from sqlalchemy import Date
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id:              Mapped[int] = mapped_column(primary_key=True, nullable=False)
    username:        Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    tg_id:           Mapped[str] = mapped_column(nullable=True)
    created_at:      Mapped[datetime] = mapped_column(Date, nullable=False)
    activated:       Mapped[bool] = mapped_column(nullable=False)

    queries: Mapped[list['Queries']] = relationship(back_populates="user")

    def __str__(self):
        return f"User {self.username}"
