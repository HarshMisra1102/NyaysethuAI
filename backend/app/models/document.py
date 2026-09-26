from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk
    from app.models.source import Source
    from app.models.user import User


class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    processing_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="completed", server_default="completed", index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    document_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    storage_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_index",
    )

    sources: Mapped[list["Source"]] = relationship(
        "Source",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="documents",
    )
