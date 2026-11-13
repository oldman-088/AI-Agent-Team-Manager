"""Initial schema metadata; execution and legacy data migration are not implemented."""
from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, Index, String, Text, text
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


class Task(Base):
    __tablename__ = 'tasks'
    __table_args__ = (CheckConstraint("status IN ('pending', 'cancelled', 'completed')", name='ck_tasks_status'), Index('uq_tasks_id_project_id', 'id', 'project_id', unique=True))
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='RESTRICT'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'pending'"))


class TaskDependency(Base):
    __tablename__ = 'task_dependencies'
    __table_args__ = (
        ForeignKeyConstraint(['task_id', 'project_id'], ['tasks.id', 'tasks.project_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['depends_on_id', 'project_id'], ['tasks.id', 'tasks.project_id'], ondelete='RESTRICT'),
        CheckConstraint('task_id != depends_on_id', name='ck_dependency_not_self'),
        Index('ix_dependencies_project_id', 'project_id'),
    )
    task_id: Mapped[int] = mapped_column(primary_key=True)
    depends_on_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(nullable=False)
