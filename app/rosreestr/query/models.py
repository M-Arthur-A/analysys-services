from datetime import datetime

from sqlalchemy import ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class Queries(Base):
    __tablename__ = "rr_queries"

    id:             Mapped[int] = mapped_column(primary_key=True)
    name:           Mapped[str] = mapped_column(nullable=True)
    user_id:        Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_ready:       Mapped[bool] = mapped_column(nullable=True)
    created_at:     Mapped[datetime] = mapped_column(Date, nullable=False)
    modified_at:    Mapped[datetime] = mapped_column(Date, nullable=False)

    user: Mapped['Users'] = relationship(back_populates="queries")
    orders: Mapped[list['Orders']] = relationship(back_populates="query")

    def __str__(self):
        return f"query #{self.id} {self.name}"


class Balance(Base):
    """
    name: last | history (every day)
    """
    __tablename__ = "rr_balance"

    id:    Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(nullable=False)
    date:  Mapped[str] = mapped_column(nullable=False)
    __table_args__ = (UniqueConstraint("date", name="rr_balance_date_key"),)


class BalanceMon(Base):
    """
    name: last | history (every day)
    """
    __tablename__ = "rr_balance_mon"

    id:    Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(nullable=False)
    date:  Mapped[str] = mapped_column(nullable=False)
    __table_args__ = (UniqueConstraint("date", name="rr_balance_mon_date_key"),)
