from datetime import datetime

from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class Monitorings(Base):
    __tablename__ = "rr_monitors"

    id:             Mapped[int] = mapped_column(primary_key=True)
    monitoringId:   Mapped[str] = mapped_column(nullable=True)
    tag:            Mapped[str] = mapped_column(nullable=True)
    cadastral:      Mapped[str] = mapped_column(nullable=True)
    user_id:        Mapped[int] = mapped_column(ForeignKey("users.id"))
    interval:       Mapped[int] = mapped_column(nullable=False)
    status:         Mapped[str] = mapped_column(nullable=True)
    status_date:    Mapped[datetime] = mapped_column(Date, nullable=True)
    status_txt:     Mapped[str] = mapped_column(nullable=True)
    error:          Mapped[str] = mapped_column(nullable=True)
    last_event_id:  Mapped[str] = mapped_column(nullable=True)
    start_at:       Mapped[datetime] = mapped_column(Date, nullable=False)
    end_at:         Mapped[datetime] = mapped_column(Date, nullable=False)
    modified_at:    Mapped[datetime] = mapped_column(Date, nullable=True)

    user: Mapped['Users'] = relationship(back_populates="monitorings")

    def __str__(self):
        return f"monitor #{self.id} {self.cadastral}"
