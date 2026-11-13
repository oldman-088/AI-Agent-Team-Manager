"""Initial schema metadata; execution and legacy data migration are not implemented."""
from sqlalchemy import CheckConstraint, ForeignKey, String, Text, text
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


class Agent(Base):
    __tablename__ = 'agents'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    instructions: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    provider: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("''"))
    model: Mapped[str] = mapped_column(String(200), nullable=False, server_default=text("''"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id', ondelete='SET NULL'), nullable=True, index=True)
