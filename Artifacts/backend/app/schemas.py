import datetime
import enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ======================================================================================
# Base Configuration & Enums
# ======================================================================================

class APIBaseModel(BaseModel):
    """Base model for all Pydantic schemas to inherit from."""
    model_config = ConfigDict(from_attributes=True)


class SystemRole(str, enum.Enum):
    ADMIN = "Admin"
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


# ======================================================================================
# Role Schemas
# ======================================================================================

class RoleBase(APIBaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the job role, e.g., 'SW Engineer'")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the role")


class RoleCreate(RoleBase):
    owner_id: Optional[int] = None


class RoleUpdate(APIBaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class RoleInDB(RoleBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner_id: Optional[int] = None


class RoleResponse(RoleInDB):
    pass


# ======================================================================================
# LCAT Schemas
# ======================================================================================

class LCATBase(APIBaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the Labor Category, e.g., 'Level 1'")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the LCAT")


class LCATCreate(LCATBase):
    owner_id: Optional[int] = None


class LCATUpdate(APIBaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class LCATInDB(LCATBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner_id: Optional[int] = None


class LCATResponse(LCATInDB):
    pass


# ======================================================================================
# User Schemas
# ======================================================================================

class UserBase(APIBaseModel):
    email: EmailStr = Field(..., description="User's unique email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    system_role: SystemRole = Field(..., description="User's role within the application for RBAC")
    is_active: bool = Field(True, description="Whether the user account is active")
    manager_id: Optional[int] = Field(
        None,
        description="Parent manager ID for employee accounts. Required when system_role is Employee.",
    )


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User's password (will be hashed on creation)")


class UserUpdate(APIBaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    system_role: Optional[SystemRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, description="New password, if changing")


class UserInDB(UserBase):
    id: int
    last_login_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserResponse(UserInDB):
    """Standard user response, without sensitive info."""
    pass


class UserSummaryResponse(APIBaseModel):
    """A minimal user representation for nesting in other schemas."""
    id: int
    full_name: str
    email: EmailStr


# ======================================================================================
# Project Schemas
# ======================================================================================

class ProjectBase(APIBaseModel):
    name: str = Field(..., min_length=3, max_length=200, description="Project name")
    code: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$", description="Unique project code (alphanumeric, dash, underscore)")
    client: Optional[str] = Field(None, max_length=100, description="Client name for the project")
    start_date: datetime.date = Field(..., description="Project start date in YYYY-MM-DD format")
    sprints: int = Field(..., gt=0, description="Duration of the project in sprints (must be positive)")
    manager_id: Optional[int] = Field(None, description="ID of the user who is the Project Manager")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Current status of the project")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(APIBaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    code: Optional[str] = Field(None, min_length=2, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    client: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime.date] = None
    sprints: Optional[int] = Field(None, gt=0)
    manager_id: Optional[int] = None
    status: Optional[ProjectStatus] = None


class ProjectInDB(ProjectBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ProjectResponse(ProjectInDB):
    """Standard project response with the manager's summary info."""
    manager: Optional[UserSummaryResponse] = None


# ======================================================================================
# Allocation Schemas
# ======================================================================================

class AllocationBase(APIBaseModel):
    project_assignment_id: int = Field(..., description="The ID of the parent project assignment")
    year: int = Field(..., ge=2020, le=2050, description="The calendar year of the allocation")
    month: int = Field(..., ge=1, le=12, description="The calendar month of the allocation (1-12)")
    allocated_hours: int = Field(..., ge=0, description="Number of hours allocated for this month")


class AllocationCreate(AllocationBase):
    pass


class AllocationUpdate(APIBaseModel):
    # Only allocated_hours can be updated. Year/month/assignment define the record.
    allocated_hours: int = Field(..., ge=0, description="Updated number of hours for this month")


class AllocationInDB(AllocationBase):
    id: int


class AllocationResponse(AllocationInDB):
    pass


class AllocationDistributionRequest(APIBaseModel):
    start_year: int = Field(..., ge=2020, le=2050)
    start_month: int = Field(..., ge=1, le=12)
    end_year: int = Field(..., ge=2020, le=2050)
    end_month: int = Field(..., ge=1, le=12)
    total_hours: Optional[int] = Field(
        None, ge=0, description="Total hours to distribute. Defaults to remaining funded hours."
    )
    strategy: Optional[str] = Field(
        "even", description="Distribution strategy identifier (currently only 'even')."
    )


# ======================================================================================
# Project Assignment Schemas
# ======================================================================================

class ProjectAssignmentBase(APIBaseModel):
    project_id: int = Field(..., description="ID of the project for this assignment")
    user_id: int = Field(..., description="ID of the user being assigned")
    role_id: int = Field(..., description="ID of the role the user will have on the project")
    lcat_id: int = Field(..., description="ID of the LCAT for this assignment")
    funded_hours: int = Field(..., ge=0, description="Total funded hours for the user on this project")


class ProjectAssignmentCreate(ProjectAssignmentBase):
    pass


class ProjectAssignmentUpdate(APIBaseModel):
    # project_id and user_id are immutable for an assignment. Create a new one if needed.
    role_id: Optional[int] = None
    lcat_id: Optional[int] = None
    funded_hours: Optional[int] = Field(None, ge=0)


class ProjectAssignmentInDB(ProjectAssignmentBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ProjectAssignmentResponse(ProjectAssignmentInDB):
    """Response for a project assignment, including nested details."""
    project: ProjectResponse
    user: UserSummaryResponse
    role: RoleResponse
    lcat: LCATResponse


class ProjectAssignmentWithAllocationsResponse(ProjectAssignmentResponse):
    """Detailed response including all monthly allocations for the assignment."""
    allocations: List[AllocationResponse] = []


# ======================================================================================
# Monthly Hour Override Schemas
# ======================================================================================

class MonthlyHourOverrideBase(APIBaseModel):
    project_id: int = Field(..., description="ID of the project this override applies to")
    year: int = Field(..., ge=2020, le=2050, description="The calendar year of the override")
    month: int = Field(..., ge=1, le=12, description="The calendar month of the override (1-12)")
    overridden_hours: int = Field(..., gt=0, description="The new total number of work hours for this month")


class MonthlyHourOverrideCreate(MonthlyHourOverrideBase):
    pass


class MonthlyHourOverrideUpdate(APIBaseModel):
    # Only overridden_hours can be updated. Year/month/project define the record.
    overridden_hours: int = Field(..., gt=0)


class MonthlyHourOverrideInDB(MonthlyHourOverrideBase):
    id: int


class MonthlyHourOverrideResponse(MonthlyHourOverrideInDB):
    pass


# ======================================================================================
# AI & Metadata Schemas
# ======================================================================================

# --- AI Recommendation Schemas ---
class AIRecommendationBase(APIBaseModel):
    recommendation_type: RecommendationType
    context_json: Optional[Dict[str, Any]] = Field(None, description="JSON blob with data used to generate the recommendation")
    recommendation_text: str = Field(..., description="The human-readable recommendation text")


class AIRecommendationCreate(AIRecommendationBase):
    pass


class AIRecommendationUpdate(APIBaseModel):
    status: Optional[RecommendationStatus] = None


class AIRecommendationInDB(AIRecommendationBase):
    id: int
    status: RecommendationStatus
    generated_at: datetime.datetime
    acted_upon_at: Optional[datetime.datetime] = None


class AIRecommendationResponse(AIRecommendationInDB):
    pass


# --- Audit Log Schemas ---
class AuditLogBase(APIBaseModel):
    action: str = Field(..., description="A code for the action performed, e.g., 'PROJECT_CREATE'")
    entity_type: Optional[str] = Field(None, description="The type of entity acted upon, e.g., 'project'")
    entity_id: Optional[int] = Field(None, description="The ID of the entity acted upon")
    details: Optional[Dict[str, Any]] = Field(None, description="JSON blob with before/after values or context")


class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = Field(None, description="ID of the user who performed the action")


class AuditLogInDB(AuditLogBase):
    id: int
    user_id: Optional[int]
    timestamp: datetime.datetime


class AuditLogResponse(AuditLogInDB):
    user: Optional[UserSummaryResponse] = None


# --- AI RAG Cache Schemas ---
class AIRagCacheBase(APIBaseModel):
    source_entity: str = Field(..., description="The source entity type, e.g., 'project'")
    source_id: int = Field(..., description="The ID of the source entity")
    document_text: str = Field(..., description="The pre-computed text document for RAG")


class AIRagCacheCreate(AIRagCacheBase):
    pass


class AIRagCacheUpdate(APIBaseModel):
    document_text: Optional[str] = None


class AIRagCacheInDB(AIRagCacheBase):
    id: int
    last_indexed_at: datetime.datetime


class AIRagCacheResponse(AIRagCacheInDB):
    pass


# ======================================================================================
# Detailed/Composite Response Schemas
# ======================================================================================

class UserWithAssignmentsResponse(UserResponse):
    """User response including all their project assignments."""
    assignments: List[ProjectAssignmentResponse] = []


class ProjectWithDetailsResponse(ProjectResponse):
    """Project response including all its assignments and overrides."""
    assignments: List[ProjectAssignmentResponse] = []
    monthly_hour_overrides: List[MonthlyHourOverrideResponse] = []
    viewers: List[UserSummaryResponse] = []


class ProjectImportResponse(APIBaseModel):
    created_projects: List[ProjectResponse] = []
    skipped_codes: List[str] = []