import datetime
import enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# --------------------------------------------------------------------------------
# ENUMS for CHECK constraints
# --------------------------------------------------------------------------------


class SystemRole(str, enum.Enum):
    ADMIN = "Admin"
    DIRECTOR = "Director"
    PM = "PM"
    EMPLOYEE = "Employee"


class ProjectStatus(str, enum.Enum):
    PLANNING = "Planning"
    ACTIVE = "Active"
    CLOSED = "Closed"
    ON_HOLD = "On Hold"


class RecommendationType(str, enum.Enum):
    STAFFING = "STAFFING"
    CONFLICT_RESOLUTION = "CONFLICT_RESOLUTION"
    FORECAST = "FORECAST"
    WORKLOAD_BALANCE = "WORKLOAD_BALANCE"


class RecommendationStatus(str, enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    DISMISSED = "Dismissed"


# --------------------------------------------------------------------------------
# CORE ENTITIES
# --------------------------------------------------------------------------------


class User(Base):
    """
    Stores information about all employees and application users.
    The system_role column is used for Role-Based Access Control (RBAC).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    system_role: Mapped[SystemRole] = mapped_column(
        String, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Relationships ---
    managed_projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="manager", foreign_keys="Project.manager_id"
    )
    assignments: Mapped[List["ProjectAssignment"]] = relationship(
        "ProjectAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user"
    )
    manager: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side=[id],
        back_populates="managed_employees",
        foreign_keys=[manager_id],
    )
    managed_employees: Mapped[List["User"]] = relationship(
        "User",
        back_populates="manager",
        foreign_keys="User.manager_id",
    )
    owned_roles: Mapped[List["Role"]] = relationship(
        "Role",
        back_populates="owner",
        foreign_keys="Role.owner_id",
    )
    owned_lcats: Mapped[List["LCAT"]] = relationship(
        "LCAT",
        back_populates="owner",
        foreign_keys="LCAT.owner_id",
    )
    granted_project_views: Mapped[List["ProjectViewer"]] = relationship(
        "ProjectViewer",
        back_populates="granted_by",
        foreign_keys="ProjectViewer.granted_by_id",
    )
    viewable_project_links: Mapped[List["ProjectViewer"]] = relationship(
        "ProjectViewer",
        back_populates="user",
        foreign_keys="ProjectViewer.user_id",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.system_role.value}')>"


class Role(Base):
    """A standardized list of job roles (e.g., 'SW Engineer', 'Data Scientist')."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    assignments: Mapped[List["ProjectAssignment"]] = relationship(
        "ProjectAssignment", back_populates="role"
    )
    owner: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="owned_roles",
        foreign_keys=[owner_id],
    )

    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_roles_owner_name"),
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"


class LCAT(Base):
    """A standardized list of Labor Categories (e.g., 'Level 1', 'Senior Consultant')."""

    __tablename__ = "lcats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    assignments: Mapped[List["ProjectAssignment"]] = relationship(
        "ProjectAssignment", back_populates="lcat"
    )
    owner: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="owned_lcats",
        foreign_keys=[owner_id],
    )

    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_lcats_owner_name"),
    )

    def __repr__(self) -> str:
        return f"<LCAT(id={self.id}, name='{self.name}')>"


class Project(Base):
    """Represents a single project with its core metadata."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    client: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    sprints: Mapped[int] = mapped_column(Integer, nullable=False)
    manager_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[ProjectStatus] = mapped_column(
        String, nullable=False, default=ProjectStatus.ACTIVE, index=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    manager: Mapped[Optional["User"]] = relationship(
        "User", back_populates="managed_projects", foreign_keys=[manager_id]
    )
    assignments: Mapped[List["ProjectAssignment"]] = relationship(
        "ProjectAssignment",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    monthly_hour_overrides: Mapped[List["MonthlyHourOverride"]] = relationship(
        "MonthlyHourOverride",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    viewer_links: Mapped[List["ProjectViewer"]] = relationship(
        "ProjectViewer",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("sprints > 0", name="ck_project_sprints_positive"),
        UniqueConstraint("manager_id", "code", name="uq_projects_manager_code"),
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, code='{self.code}', name='{self.name}')>"


class ProjectAssignment(Base):
    """
    Represents an employee being staffed on a project, including their role,
    LCAT, and total funded hours for that project.
    """

    __tablename__ = "project_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    lcat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lcats.id", ondelete="RESTRICT"), nullable=False
    )
    funded_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    project: Mapped["Project"] = relationship("Project", back_populates="assignments")
    user: Mapped["User"] = relationship("User", back_populates="assignments")
    role: Mapped["Role"] = relationship("Role", back_populates="assignments")
    lcat: Mapped["LCAT"] = relationship("LCAT", back_populates="assignments")
    allocations: Mapped[List["Allocation"]] = relationship(
        "Allocation",
        back_populates="project_assignment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user"),
        CheckConstraint("funded_hours >= 0", name="ck_assignment_funded_hours_nonnegative"),
    )

    def __repr__(self) -> str:
        return f"<ProjectAssignment(id={self.id}, project_id={self.project_id}, user_id={self.user_id})>"


class Allocation(Base):
    """
    Stores the number of hours an employee is allocated for a specific month
    on a specific project assignment.
    """

    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_assignment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("project_assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    allocated_hours: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- Relationships ---
    project_assignment: Mapped["ProjectAssignment"] = relationship(
        "ProjectAssignment", back_populates="allocations"
    )

    __table_args__ = (
        UniqueConstraint(
            "project_assignment_id", "year", "month", name="uq_assignment_year_month"
        ),
        CheckConstraint("month >= 1 AND month <= 12", name="ck_allocation_month_range"),
        CheckConstraint(
            "allocated_hours >= 0", name="ck_allocation_hours_nonnegative"
        ),
        Index("idx_allocations_year_month", "year", "month"),
        Index(
            "idx_allocations_assignment",
            "project_assignment_id",
        ),
    )

    def __repr__(self) -> str:
        return f"<Allocation(id={self.id}, assignment_id={self.project_assignment_id}, date={self.year}-{self.month:02d}, hours={self.allocated_hours})>"


class MonthlyHourOverride(Base):
    """
    Stores project-specific overrides for the standard number of work hours in a month.
    """

    __tablename__ = "monthly_hour_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    overridden_hours: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- Relationships ---
    project: Mapped["Project"] = relationship(
        "Project", back_populates="monthly_hour_overrides"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "year", "month", name="uq_override_project_year_month"),
        CheckConstraint("month >= 1 AND month <= 12", name="ck_override_month_range"),
        CheckConstraint("overridden_hours > 0", name="ck_override_hours_positive"),
        Index("idx_monthly_hour_overrides_project_year_month", "project_id", "year", "month"),
    )

    def __repr__(self) -> str:
        return f"<MonthlyHourOverride(id={self.id}, project_id={self.project_id}, date={self.year}-{self.month:02d}, hours={self.overridden_hours})>"


# --------------------------------------------------------------------------------
# PROJECT SHARING TABLES
# --------------------------------------------------------------------------------


class ProjectViewer(Base):
    """Associates additional users who can view a project without edit rights."""

    __tablename__ = "project_viewers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    granted_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="viewer_links")
    user: Mapped["User"] = relationship(
        "User",
        back_populates="viewable_project_links",
        foreign_keys=[user_id],
    )
    granted_by: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="granted_project_views",
        foreign_keys=[granted_by_id],
    )

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_viewers_project_user"),
    )

    def __repr__(self) -> str:
        return (
            f"<ProjectViewer(id={self.id}, project_id={self.project_id}, user_id={self.user_id})>"
        )


# --------------------------------------------------------------------------------
# AI & METADATA TABLES
# --------------------------------------------------------------------------------


class AIRagCache(Base):
    """
    Stores pre-computed text documents for the Retrieval-Augmented Generation (RAG) feature.
    """

    __tablename__ = "ai_rag_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_entity: Mapped[str] = mapped_column(String, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    document_text: Mapped[str] = mapped_column(String, nullable=False)
    last_indexed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("source_entity", "source_id", name="uq_rag_source"),
        Index("idx_ai_rag_cache_source", "source_entity", "source_id"),
    )

    def __repr__(self) -> str:
        return f"<AIRagCache(id={self.id}, source='{self.source_entity}:{self.source_id}')>"


class AIRecommendation(Base):
    """
    A generic table to store outputs from the AI agent, such as staffing recommendations.
    """

    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_type: Mapped[RecommendationType] = mapped_column(
        String, nullable=False
    )
    context_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recommendation_text: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[RecommendationStatus] = mapped_column(
        String, nullable=False, default=RecommendationStatus.PENDING
    )
    generated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    acted_upon_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True
    )

    def __repr__(self) -> str:
        return f"<AIRecommendation(id={self.id}, type='{self.recommendation_type.value}', status='{self.status.value}')>"


class AuditLog(Base):
    """A simple audit trail for significant events in the system."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String, nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )

    # --- Relationships ---
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    __table_args__ = (Index("idx_audit_log_entity", "entity_type", "entity_id"),)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, timestamp='{self.timestamp}')>"