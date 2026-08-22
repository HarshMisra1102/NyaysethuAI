from sqlalchemy import Text, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Scheme(TimestampMixin, Base):
    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    eligibility_rules: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    application_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )