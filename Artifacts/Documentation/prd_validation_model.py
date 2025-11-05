from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class UserStory(BaseModel):
    """
    Represents a single user story within the PRD.
    """
    id: str = Field(..., description="Unique identifier for the user story (e.g., US-001).")
    persona: str = Field(..., description="The user persona performing the action (e.g., 'As a registered user').")
    user_story: str = Field(..., description="The user story itself (e.g., 'I want to log in so that I can access my dashboard').")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria that define when the user story is complete.")

class GoalMetric(BaseModel):
    """
    Represents a strategic goal with its associated Key Performance Indicator (KPI) and target.
    """
    goal: str = Field(..., description="The strategic goal this requirement contributes to.")
    kpi: str = Field(..., description="Key Performance Indicator used to measure success for this goal.")
    target: str = Field(..., description="The specific target value or range for the KPI.")

class ProductRequirementsDocument(BaseModel):
    """
    Pydantic model for validating Product Requirements Documents based on a defined structure.
    """

    # 1. Executive Summary & Vision
    product_name: str = Field(..., description="The official name of the product.")
    overview: str = Field(..., description="A brief summary of the product, its core functionality, and its purpose.")
    purpose: str = Field(..., description="The core problem the product aims to solve or the value it provides.")
    vision: str = Field(..., description="The long-term aspirational goal and future state for the product.")

    # 2. The Problem
    problem_statement: str = Field(..., description="A clear and concise description of the problem the product aims to solve for its users or market.")
    user_personas_scenarios: List[str] = Field(..., description="Descriptions of key user personas and their typical scenarios or pain points that the product addresses.")

    # 3. Goals & Success Metrics
    goals_metrics: List[GoalMetric] = Field(..., description="A list of strategic goals, each with an associated KPI and target metric to measure success.")

    # 4. Functional Requirements & User Stories
    functional_requirements: Dict[str, List[UserStory]] = Field(
        ...,
        description="Functional requirements organized by Epic. Each Epic (key) contains a list of detailed user stories (value)."
    )

    # 5. Non-Functional Requirements (NFRs)
    non_functional_requirements: Dict[str, str] = Field(
        ...,
        description="A dictionary of Non-Functional Requirements. Keys are NFR types (e.g., 'Performance', 'Security', 'Accessibility', 'Scalability', 'Usability', 'Reliability') and values are their detailed descriptions."
    )

    # 6. Technical Considerations
    tech_stack_recommendations: Optional[List[str]] = Field(
        None,
        description="Recommended technology stack components (e.g., programming languages, frameworks, cloud providers)."
    )
    database_design_considerations: Optional[str] = Field(
        None,
        description="Key considerations and recommendations for the database design (e.g., type, schema principles, data models)."
    )
    api_design_principles: Optional[List[str]] = Field(
        None,
        description="Guiding principles and recommendations for API design (e.g., RESTful, GraphQL, authentication)."
    )

    # 7. Release Plan & Milestones
    mvp_features: List[str] = Field(..., description="A list of essential features planned for the Minimum Viable Product (MVP).")
    future_versions: Optional[List[str]] = Field(
        None,
        description="Features, enhancements, or plans for subsequent product versions beyond the MVP."
    )

    # 8. Out of Scope & Future Considerations
    out_of_scope_v1: Optional[List[str]] = Field(
        None,
        description="Features or functionalities explicitly excluded from the initial release (V1.0) to manage scope."
    )
    future_work: Optional[List[str]] = Field(
        None,
        description="Ideas, potential features, or considerations for future development that are not yet committed."
    )

    # 9. Appendix & Open Questions
    open_questions: Optional[List[str]] = Field(
        None,
        description="Any unresolved questions, decisions pending, or areas requiring further discussion."
    )
    dependencies_assumptions: Optional[List[str]] = Field(
        None,
        description="List of external dependencies (e.g., third-party services, other teams) and underlying assumptions made for the project."
    )