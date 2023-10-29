from datetime import datetime

from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class Orders(Base):
    __tablename__ = "rr_orders"

    id:             Mapped[str] = mapped_column(primary_key=True)
    query_id:       Mapped[int] = mapped_column(ForeignKey("rr_queries.id"))
    session_id:     Mapped[str] = mapped_column(nullable=True)
    cadastral:      Mapped[str] = mapped_column(nullable=False)
    cadastral_type: Mapped[str] = mapped_column(nullable=False)
    status:         Mapped[str] = mapped_column(nullable=True)
    status_txt:     Mapped[str] = mapped_column(nullable=True)
    is_ready:       Mapped[bool] = mapped_column(nullable=True)
    created_at:     Mapped[datetime] = mapped_column(Date, nullable=False)
    modified_at:    Mapped[datetime] = mapped_column(Date, nullable=False)

    query: Mapped['Queries'] = relationship(back_populates="orders")

    def __str__(self):
        return f"order #{self.id} {self.cadastral_type}{self.cadastral}"

