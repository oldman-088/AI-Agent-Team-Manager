"""Initial schema metadata; execution and legacy data migration are not implemented."""
from sqlalchemy import CheckConstraint, String, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (CheckConstraint("status IN ('planned', 'active', 'paused', 'completed', 'archived')", name='ck_projects_status'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'planned'"))
