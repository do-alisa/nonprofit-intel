from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    ein: Mapped[str] = mapped_column(String(9), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2), index=True)
    ntee_code: Mapped[str | None] = mapped_column(String(10))
    subsection: Mapped[str | None] = mapped_column(String(5))
    ruling_year: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    filings: Mapped[list["Filing"]] = relationship(back_populates="organization")


class Filing(Base):
    __tablename__ = "filings"
    __table_args__ = (
        Index("ix_filings_org_year", "organization_id", "tax_year", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    tax_year: Mapped[int]
    form_type: Mapped[str | None] = mapped_column(String(10))

    total_revenue: Mapped[int | None] = mapped_column(BigInteger)
    total_expenses: Mapped[int | None] = mapped_column(BigInteger)
    total_assets: Mapped[int | None] = mapped_column(BigInteger)
    total_liabilities: Mapped[int | None] = mapped_column(BigInteger)
    contributions: Mapped[int | None] = mapped_column(BigInteger)
    program_revenue: Mapped[int | None] = mapped_column(BigInteger)
    program_expenses: Mapped[int | None] = mapped_column(BigInteger)
    admin_expenses: Mapped[int | None] = mapped_column(BigInteger)
    fundraising_expenses: Mapped[int | None] = mapped_column(BigInteger)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    organization: Mapped[Organization] = relationship(back_populates="filings")