from datetime import datetime

from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class OrdersFr(Base):
    __tablename__ = "fr_orders"

    id:             Mapped[int] = mapped_column(primary_key=True)
    query_id:       Mapped[str] = mapped_column(nullable=False)
    inn:            Mapped[str] = mapped_column(nullable=True)
    user_id:        Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_ready:       Mapped[bool] = mapped_column(nullable=True)
    created_at:     Mapped[datetime] = mapped_column(Date, nullable=False)

    user: Mapped['Users'] = relationship(back_populates="fr_orders")

    def __str__(self):
        return f"query #{self.id} {self.inn}"
