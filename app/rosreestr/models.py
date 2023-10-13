from datetime import datetime

from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class Orders(Base):
    __tablename__ = "rr_orders"

    id:             Mapped[int] = mapped_column(primary_key=True)
    query_id:       Mapped[int] = mapped_column(ForeignKey("rr_queries.id"))
    cadastral:      Mapped[int] = mapped_column(nullable=False)
    cadastral_type: Mapped[str] = mapped_column(nullable=False)
    status:         Mapped[str] = mapped_column(nullable=True)
    is_ready:       Mapped[bool] = mapped_column(nullable=True)
    created_at:     Mapped[datetime] = mapped_column(Date, nullable=False)
    modified_at:    Mapped[datetime] = mapped_column(Date, nullable=False)

    user:  Mapped['Users'] = relationship(back_populates="orders")
    query: Mapped['Queries'] = relationship(back_populates="orders")

    def __str__(self):
        return f"order #{self.id} {self.cadastral_type}{self.cadastral}"

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
