"""
Comprehensive tests for manager-specific data isolation.

This test suite verifies that:
1. Each manager sees only their own data
2. No cross-contamination between managers
3. All API endpoints enforce manager filtering
4. Manager-scoped queries return correct results
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app import crud, models, schemas
from app.core import security

client = TestClient(app)


class TestManagerDataIsolation:
    """Test suite for verifying complete data isolation between managers."""

    def test_managers_cannot_see_each_others_projects(self, db_session: Session):
        """Verify that managers cannot see projects belonging to other managers."""
        # Get two different managers
        managers = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).limit(2).all()
        assert len(managers) >= 2, "Need at least 2 managers for isolation testing"
        
        manager1_id = managers[0].id
        manager2_id = managers[1].id
        
        # Get projects for manager 1
        manager1_projects = crud.get_projects(db_session, manager_id=manager1_id)
        
        # Get projects for manager 2
        manager2_projects = crud.get_projects(db_session, manager_id=manager2_id)
        
        # Extract project IDs
        manager1_project_ids = {p.id for p in manager1_projects}
        manager2_project_ids = {p.id for p in manager2_projects}
        
        # Verify no overlap
        assert len(manager1_project_ids & manager2_project_ids) == 0, \
            "Managers should not see each other's projects"
        
        # Verify each manager has projects
        assert len(manager1_projects) > 0, "Manager 1 should have projects"
        assert len(manager2_projects) > 0, "Manager 2 should have projects"

    def test_managers_cannot_see_each_others_employees(self, db_session: Session):
        """Verify that managers cannot see employees belonging to other managers."""
        managers = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).limit(2).all()
        assert len(managers) >= 2
        
        manager1_id = managers[0].id
        manager2_id = managers[1].id
        
        # Get employees for each manager
        manager1_employees = crud.get_users(db_session, manager_id=manager1_id, system_role=models.SystemRole.EMPLOYEE)
        manager2_employees = crud.get_users(db, manager_id=manager2_id, system_role=models.SystemRole.EMPLOYEE)
        
        # Extract employee IDs
        manager1_employee_ids = {e.id for e in manager1_employees}
        manager2_employee_ids = {e.id for e in manager2_employees}
        
        # Verify no overlap
        assert len(manager1_employee_ids & manager2_employee_ids) == 0, \
            "Managers should not see each other's employees"
        
        # Verify each manager has employees
        assert len(manager1_employees) > 0
        assert len(manager2_employees) > 0

    def test_managers_cannot_see_each_others_roles(self, db_session: Session):
        """Verify that managers cannot see roles belonging to other managers."""
        managers = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).limit(2).all()
        assert len(managers) >= 2
        
        manager1_id = managers[0].id
        manager2_id = managers[1].id
        
        # Get roles for each manager
        manager1_roles = crud.get_roles(db_session, owner_id=manager1_id)
        manager2_roles = crud.get_roles(db, owner_id=manager2_id)
        
        # Extract role IDs
        manager1_role_ids = {r.id for r in manager1_roles}
        manager2_role_ids = {r.id for r in manager2_roles}
        
        # Verify no overlap
        assert len(manager1_role_ids & manager2_role_ids) == 0, \
            "Managers should not see each other's roles"
        
        # Verify each manager has roles
        assert len(manager1_roles) > 0
        assert len(manager2_roles) > 0

    def test_managers_cannot_see_each_others_lcats(self, db_session: Session):
        """Verify that managers cannot see LCATs belonging to other managers."""
        managers = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).limit(2).all()
        assert len(managers) >= 2
        
        manager1_id = managers[0].id
        manager2_id = managers[1].id
        
        # Get LCATs for each manager
        manager1_lcats = crud.get_lcats(db_session, owner_id=manager1_id)
        manager2_lcats = crud.get_lcats(db, owner_id=manager2_id)
        
        # Extract LCAT IDs
        manager1_lcat_ids = {l.id for l in manager1_lcats}
        manager2_lcat_ids = {l.id for l in manager2_lcats}
        
        # Verify no overlap
        assert len(manager1_lcat_ids & manager2_lcat_ids) == 0, \
            "Managers should not see each other's LCATs"
        
        # Verify each manager has LCATs
        assert len(manager1_lcats) > 0
        assert len(manager2_lcats) > 0

    def test_projects_api_requires_manager_id(self):
        """Verify that projects API returns error without manager_id."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 422, "Should require manager_id parameter"

    def test_employees_api_requires_manager_id(self):
        """Verify that employees API returns error without manager_id."""
        response = client.get("/api/v1/employees")
        assert response.status_code == 422, "Should require manager_id parameter"

    def test_roles_api_requires_owner_id(self):
        """Verify that roles API returns error without owner_id."""
        response = client.get("/api/v1/admin/roles/")
        assert response.status_code == 422, "Should require owner_id parameter"

    def test_lcats_api_requires_owner_id(self):
        """Verify that LCATs API returns error without owner_id."""
        response = client.get("/api/v1/admin/lcats/")
        assert response.status_code == 422, "Should require owner_id parameter"

    def test_portfolio_dashboard_requires_manager_id(self):
        """Verify that portfolio dashboard API requires manager_id."""
        response = client.get("/api/v1/reports/portfolio-dashboard")
        assert response.status_code == 422, "Should require manager_id parameter"

    def test_portfolio_dashboard_scoped_to_manager(self, db_session: Session):
        """Verify portfolio dashboard only shows manager's data."""
        # Get a manager
        manager = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).first()
        assert manager is not None
        
        # Get manager's projects count
        manager_projects = crud.get_projects(db_session, manager_id=manager.id)
        expected_project_count = len(manager_projects)
        
        # Call portfolio dashboard API
        response = client.get(f"/api/v1/reports/portfolio-dashboard?manager_id={manager.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_projects"] == expected_project_count, \
            "Dashboard should only show manager's projects"

    def test_manager_allocations_endpoint_works(self, db_session: Session):
        """Test the new manager allocations rollup endpoint."""
        manager = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).first()
        assert manager is not None
        
        # Call manager allocations API
        response = client.get(
            "/api/v1/reports/manager-allocations",
            params={
                "manager_id": manager.id,
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 12
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "employees" in data
        assert "date_range" in data
        assert isinstance(data["employees"], list)
        
        # If manager has employees, verify data structure
        if len(data["employees"]) > 0:
            employee = data["employees"][0]
            assert "employee_id" in employee
            assert "employee_name" in employee
            assert "total_funded_hours" in employee
            assert "monthly_totals" in employee

    def test_allocations_scoped_to_manager_projects(self, db_session: Session):
        """Verify that allocation summaries only include manager's project data."""
        managers = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).limit(2).all()
        assert len(managers) >= 2
        
        manager1_id = managers[0].id
        manager2_id = managers[1].id
        
        # Get monthly totals for each manager
        manager1_totals = crud.get_monthly_user_allocation_totals(db_session, manager_id=manager1_id)
        manager2_totals = crud.get_monthly_user_allocation_totals(db_session, manager_id=manager2_id)
        
        # Get employees for each manager
        manager1_employees = crud.get_users(db_session, manager_id=manager1_id, system_role=models.SystemRole.EMPLOYEE)
        manager2_employees = crud.get_users(db_session, manager_id=manager2_id, system_role=models.SystemRole.EMPLOYEE)
        
        manager1_employee_ids = {e.id for e in manager1_employees}
        manager2_employee_ids = {e.id for e in manager2_employees}
        
        # Verify manager1's totals only include their employees
        for total in manager1_totals:
            assert total["user_id"] in manager1_employee_ids, \
                "Manager 1's allocation totals should only include their employees"
        
        # Verify manager2's totals only include their employees
        for total in manager2_totals:
            assert total["user_id"] in manager2_employee_ids, \
                "Manager 2's allocation totals should only include their employees"

    def test_no_director_role_exists(self, db_session: Session):
        """Verify that no users have Director role."""
        # This would fail if Director role still exists in enum
        from app.models import SystemRole
        
        # Verify Director is not in enum
        roles = [r.value for r in SystemRole]
        assert "Director" not in roles, "Director role should be removed from enum"
        
        # Verify no users have Director as string (database level)
        director_users = db_session.query(models.User).filter(models.User.system_role == "Director").count()
        assert director_users == 0, "No users should have Director role"

    def test_all_employees_have_manager(self, db_session: Session):
        """Verify all employee users have a manager_id set."""
        employees = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.EMPLOYEE).all()
        
        for employee in employees:
            assert employee.manager_id is not None, \
                f"Employee {employee.full_name} should have a manager_id"

    def test_all_roles_have_owner(self, db_session: Session):
        """Verify all roles have an owner_id set."""
        roles = db_session.query(models.Role).all()
        
        for role in roles:
            assert role.owner_id is not None, \
                f"Role {role.name} should have an owner_id"

    def test_all_lcats_have_owner(self, db_session: Session):
        """Verify all LCATs have an owner_id set."""
        lcats = db_session.query(models.LCAT).all()
        
        for lcat in lcats:
            assert lcat.owner_id is not None, \
                f"LCAT {lcat.name} should have an owner_id"

    def test_all_projects_have_manager(self, db_session: Session):
        """Verify all projects have a manager_id set."""
        projects = db_session.query(models.Project).all()
        
        for project in projects:
            assert project.manager_id is not None, \
                f"Project {project.name} should have a manager_id"


class TestManagerWorkflows:
    """Test complete workflows for managers."""

    def test_create_project_workflow(self, db_session: Session):
        """Test that a manager can create a project and it's properly scoped."""
        # Get a manager
        manager = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).first()
        assert manager is not None
        
        # Create a project
        project = crud.create_project(
            db_session,
            schemas.ProjectCreate(
                name="Test Isolation Project",
                code=f"TEST-ISO-{manager.id}",
                client="Test Client",
                start_date="2026-01-01",
                sprints=10,
                manager_id=manager.id,
                status="Active"
            )
        )
        
        # Verify project is owned by manager
        assert project.manager_id == manager.id
        
        # Verify project appears in manager's list
        manager_projects = crud.get_projects(db_session, manager_id=manager.id)
        assert project.id in [p.id for p in manager_projects]
        
        # Get another manager
        other_managers = db_session.query(models.User).filter(
            models.User.system_role == models.SystemRole.PM,
            models.User.id != manager.id
        ).first()
        
        if other_managers:
            # Verify project does NOT appear in other manager's list
            other_projects = crud.get_projects(db_session, manager_id=other_managers.id)
            assert project.id not in [p.id for p in other_projects]

    def test_create_employee_workflow(self, db_session: Session):
        """Test that employees are properly assigned to their manager."""
        # Get a manager
        manager = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).first()
        assert manager is not None
        
        # Create an employee
        password_hash = security.get_password_hash("testpass123")
        employee = crud.create_user(
            db_session,
            schemas.UserCreate(
                email=f"test.employee.{manager.id}@test.com",
                full_name="Test Employee",
                system_role=models.SystemRole.EMPLOYEE,
                is_active=True,
                manager_id=manager.id,
                password="testpass123"
            ),
            password_hash=password_hash
        )
        
        # Verify employee is assigned to manager
        assert employee.manager_id == manager.id
        
        # Verify employee appears in manager's list
        manager_employees = crud.get_users(db_session, manager_id=manager.id, system_role=models.SystemRole.EMPLOYEE)
        assert employee.id in [e.id for e in manager_employees]
        
        # Get another manager
        other_manager = db_session.query(models.User).filter(
            models.User.system_role == models.SystemRole.PM,
            models.User.id != manager.id
        ).first()
        
        if other_manager:
            # Verify employee does NOT appear in other manager's list
            other_employees = crud.get_users(db_session, manager_id=other_manager.id, system_role=models.SystemRole.EMPLOYEE)
            assert employee.id not in [e.id for e in other_employees]

    def test_role_creation_scoped_to_manager(self, db_session: Session):
        """Test that roles are scoped to the manager who creates them."""
        # Get a manager
        manager = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).first()
        assert manager is not None
        
        # Create a role
        role = crud.create_role(
            db_session,
            schemas.RoleCreate(
                name=f"Test Role M{manager.id}",
                description="Test role for isolation",
                owner_id=manager.id
            ),
            owner_id=manager.id
        )
        
        # Verify role is owned by manager
        assert role.owner_id == manager.id
        
        # Verify role appears in manager's list
        manager_roles = crud.get_roles(db_session, owner_id=manager.id)
        assert role.id in [r.id for r in manager_roles]
        
        # Get another manager
        other_manager = db_session.query(models.User).filter(
            models.User.system_role == models.SystemRole.PM,
            models.User.id != manager.id
        ).first()
        
        if other_manager:
            # Verify role does NOT appear in other manager's list
            other_roles = crud.get_roles(db_session, owner_id=other_manager.id)
            assert role.id not in [r.id for r in other_roles]


class TestAPIEndpointIsolation:
    """Test API endpoints enforce manager isolation."""

    def test_projects_api_filters_by_manager(self, db_session: Session):
        """Test GET /projects endpoint enforces manager filtering."""
        # Get two managers
        managers = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).limit(2).all()
        assert len(managers) >= 2
        
        manager1_id = managers[0].id
        manager2_id = managers[1].id
        
        # Request projects for manager 1
        response1 = client.get(f"/api/v1/projects?manager_id={manager1_id}")
        assert response1.status_code == 200
        projects1 = response1.json()
        
        # Request projects for manager 2
        response2 = client.get(f"/api/v1/projects?manager_id={manager2_id}")
        assert response2.status_code == 200
        projects2 = response2.json()
        
        # Extract project IDs
        project_ids1 = {p["id"] for p in projects1}
        project_ids2 = {p["id"] for p in projects2}
        
        # Verify no overlap
        assert len(project_ids1 & project_ids2) == 0

    def test_employees_api_filters_by_manager(self, db_session: Session):
        """Test GET /employees endpoint enforces manager filtering."""
        managers = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).limit(2).all()
        assert len(managers) >= 2
        
        manager1_id = managers[0].id
        manager2_id = managers[1].id
        
        # Request employees for manager 1
        response1 = client.get(f"/api/v1/employees?manager_id={manager1_id}")
        assert response1.status_code == 200
        employees1 = response1.json()
        
        # Request employees for manager 2
        response2 = client.get(f"/api/v1/employees?manager_id={manager2_id}")
        assert response2.status_code == 200
        employees2 = response2.json()
        
        # Extract employee IDs
        employee_ids1 = {e["id"] for e in employees1}
        employee_ids2 = {e["id"] for e in employees2}
        
        # Verify no overlap
        assert len(employee_ids1 & employee_ids2) == 0

    def test_manager_allocations_endpoint(self, db_session: Session):
        """Test new manager allocations rollup endpoint."""
        manager = db_session.query(models.User).filter(models.User.system_role == models.SystemRole.PM).first()
        assert manager is not None
        
        response = client.get(
            "/api/v1/reports/manager-allocations",
            params={
                "manager_id": manager.id,
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "employees" in data
        assert "date_range" in data
        
        # Verify date range
        assert data["date_range"]["start_year"] == 2025
        assert data["date_range"]["start_month"] == 1
        assert data["date_range"]["end_year"] == 2026
        assert data["date_range"]["end_month"] == 12
        
        # Verify all employees belong to this manager
        manager_employees = crud.get_users(db_session, manager_id=manager.id, system_role=models.SystemRole.EMPLOYEE)
        manager_employee_ids = {e.id for e in manager_employees}
        
        for emp_data in data["employees"]:
            assert emp_data["employee_id"] in manager_employee_ids, \
                "Rollup should only include manager's employees"


def test_no_project_viewer_endpoints_exist():
    """Verify ProjectViewer endpoints have been removed."""
    # These should not exist anymore
    test_responses = [
        client.get("/api/v1/projects/1/viewers"),
        client.post("/api/v1/projects/1/viewers", json={"project_id": 1, "user_id": 1}),
        client.delete("/api/v1/projects/1/viewers/1")
    ]
    
    for response in test_responses:
        # Should be 404 (not found) not 200/201
        assert response.status_code in [404, 405], \
            "ProjectViewer endpoints should be removed"

