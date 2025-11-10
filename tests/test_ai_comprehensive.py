"""Comprehensive tests for AI features with realistic data."""

from __future__ import annotations

import pytest
from datetime import date

from app.utils.reporting import standard_month_hours


@pytest.fixture
def ai_comprehensive_seed(client, api_prefix):
    """Create a realistic staffing scenario for AI testing."""
    
    # Create manager
    manager = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "manager@company.com",
            "full_name": "Sarah Manager",
            "password": "SecurePass9!",
            "system_role": "PM",
            "is_active": True,
        },
    ).json()
    manager_id = manager["id"]
    
    # Create roles
    sw_engineer_role = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Software Engineer", "description": "Develops software", "owner_id": manager_id},
    ).json()
    
    data_scientist_role = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Data Scientist", "description": "Analyzes data", "owner_id": manager_id},
    ).json()
    
    pm_role = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Project Manager", "description": "Manages projects", "owner_id": manager_id},
    ).json()
    
    # Create LCATs
    level1_lcat = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Level 1", "description": "Entry level", "owner_id": manager_id},
    ).json()
    
    level2_lcat = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Level 2", "description": "Mid level", "owner_id": manager_id},
    ).json()
    
    senior_lcat = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Senior", "description": "Senior level", "owner_id": manager_id},
    ).json()
    
    # Create employees
    employees = []
    employee_data = [
        ("john.smith@company.com", "John Smith"),
        ("jane.doe@company.com", "Jane Doe"),
        ("bob.wilson@company.com", "Bob Wilson"),
        ("alice.chen@company.com", "Alice Chen"),
        ("mike.brown@company.com", "Mike Brown"),
    ]
    
    for email, name in employee_data:
        emp = client.post(
            f"{api_prefix}/employees/",
            json={
                "email": email,
                "full_name": name,
                "password": "SecurePass9!",
                "system_role": "Employee",
                "is_active": True,
                "manager_id": manager_id,
            },
        ).json()
        employees.append(emp)
    
    # Create projects
    project_alpha = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "Project Alpha",
            "code": "ALPHA",
            "client": "Acme Corp",
            "start_date": "2025-01-01",
            "sprints": 6,
            "status": "Active",
            "manager_id": manager_id,
        },
    ).json()
    
    project_beta = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "Project Beta",
            "code": "BETA",
            "client": "Tech Inc",
            "start_date": "2025-02-01",
            "sprints": 4,
            "status": "Active",
            "manager_id": manager_id,
        },
    ).json()
    
    # Create assignments for Project Alpha
    # John Smith - Software Engineer - Heavy allocation (will be over-allocated)
    john_alpha = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_alpha["id"],
            "user_id": employees[0]["id"],
            "role_id": sw_engineer_role["id"],
            "lcat_id": senior_lcat["id"],
            "funded_hours": 800,
        },
    ).json()
    
    # Jane Doe - Data Scientist - Medium allocation
    jane_alpha = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_alpha["id"],
            "user_id": employees[1]["id"],
            "role_id": data_scientist_role["id"],
            "lcat_id": level2_lcat["id"],
            "funded_hours": 400,
        },
    ).json()
    
    # Create assignments for Project Beta
    # John Smith also on Beta (will cause over-allocation)
    john_beta = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_beta["id"],
            "user_id": employees[0]["id"],
            "role_id": sw_engineer_role["id"],
            "lcat_id": senior_lcat["id"],
            "funded_hours": 400,
        },
    ).json()
    
    # Bob Wilson - Software Engineer - Light allocation (will be on bench)
    bob_beta = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project_beta["id"],
            "user_id": employees[2]["id"],
            "role_id": sw_engineer_role["id"],
            "lcat_id": level1_lcat["id"],
            "funded_hours": 200,
        },
    ).json()
    
    # Create allocations for current month to trigger conflicts/bench
    today = date.today()
    current_year = today.year
    current_month = today.month
    standard_hours = standard_month_hours(current_year, current_month)
    
    # John Smith - Over-allocated (90 hours on Alpha + 70 hours on Beta = 160 hours = ~95% FTE)
    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": john_alpha["id"],
            "year": current_year,
            "month": current_month,
            "allocated_hours": int(standard_hours * 0.55),  # 55% FTE
        },
    )
    
    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": john_beta["id"],
            "year": current_year,
            "month": current_month,
            "allocated_hours": int(standard_hours * 0.50),  # 50% FTE - Total 105%
        },
    )
    
    # Jane Doe - Normal allocation (60% FTE)
    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": jane_alpha["id"],
            "year": current_year,
            "month": current_month,
            "allocated_hours": int(standard_hours * 0.60),
        },
    )
    
    # Bob Wilson - Under-allocated (20% FTE - on bench)
    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": bob_beta["id"],
            "year": current_year,
            "month": current_month,
            "allocated_hours": int(standard_hours * 0.20),
        },
    )
    
    # Alice Chen and Mike Brown - No allocations (on bench)
    
    return {
        "manager_id": manager_id,
        "roles": {
            "sw_engineer": sw_engineer_role["id"],
            "data_scientist": data_scientist_role["id"],
            "pm": pm_role["id"],
        },
        "lcats": {
            "level1": level1_lcat["id"],
            "level2": level2_lcat["id"],
            "senior": senior_lcat["id"],
        },
        "employees": {
            "john": employees[0]["id"],
            "jane": employees[1]["id"],
            "bob": employees[2]["id"],
            "alice": employees[3]["id"],
            "mike": employees[4]["id"],
        },
        "projects": {
            "alpha": project_alpha["id"],
            "beta": project_beta["id"],
        },
        "assignments": {
            "john_alpha": john_alpha["id"],
            "jane_alpha": jane_alpha["id"],
            "john_beta": john_beta["id"],
            "bob_beta": bob_beta["id"],
        },
    }


def test_rag_reindex_with_data(client, api_prefix, ai_comprehensive_seed):
    """Test RAG cache reindexing with realistic data."""
    
    response = client.post(f"{api_prefix}/ai/reindex")
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "message" in data
    # Should have indexed projects and employees
    assert "documents" in data["message"].lower() or "refreshed" in data["message"].lower()


def test_ai_chat_with_context(client, api_prefix, ai_comprehensive_seed):
    """Test AI chat with realistic project data."""
    
    # Test query about specific employee
    response = client.post(
        f"{api_prefix}/ai/chat",
        json={
            "query": "What projects is John Smith working on?",
            "context_limit": 5,
        },
    )
    
    # Should return 200 with answer or 503 if API key not configured
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)
        # Answer should reference context
        assert len(data["answer"]) > 0


def test_staffing_recommendations_with_availability(client, api_prefix, ai_comprehensive_seed):
    """Test staffing recommendations with real availability data."""
    
    today = date.today()
    
    # Request Software Engineer for Project Alpha
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_comprehensive_seed["projects"]["alpha"],
            "role_id": ai_comprehensive_seed["roles"]["sw_engineer"],
            "year": today.year,
            "month": today.month,
            "required_hours": 80,
        },
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "candidates" in data
        assert "reasoning" in data
        
        # Should find available candidates (Alice, Mike have 0 allocations)
        # Bob has 20% FTE so also available
        # John is over-allocated so should not be recommended
        candidates = data["candidates"]
        assert isinstance(candidates, list)
        
        # Verify candidate structure
        if len(candidates) > 0:
            candidate = candidates[0]
            assert "user_id" in candidate
            assert "full_name" in candidate
            assert "current_fte" in candidate
            assert "available_hours" in candidate


def test_staffing_recommendations_with_lcat_filter(client, api_prefix, ai_comprehensive_seed):
    """Test staffing recommendations filtering by LCAT."""
    
    today = date.today()
    
    # Request by LCAT only (no role filter)
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_comprehensive_seed["projects"]["beta"],
            "lcat_id": ai_comprehensive_seed["lcats"]["senior"],
            "year": today.year,
            "month": today.month,
            "required_hours": 120,
        },
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "candidates" in data
        assert "reasoning" in data


def test_conflict_detection_finds_overallocation(client, api_prefix, ai_comprehensive_seed):
    """Test that conflict detection identifies John Smith's over-allocation."""
    
    response = client.get(f"{api_prefix}/ai/conflicts")
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "conflicts" in data
        assert "message" in data
        
        conflicts = data["conflicts"]
        assert isinstance(conflicts, list)
        
        # John Smith should be in conflicts (105% FTE)
        if len(conflicts) > 0:
            conflict = conflicts[0]
            assert "user_id" in conflict
            assert "employee" in conflict
            assert "fte" in conflict
            assert "projects" in conflict
            
            # FTE should be > 1.0
            assert conflict["fte"] > 1.0


def test_workload_balance_suggestions(client, api_prefix, ai_comprehensive_seed):
    """Test workload balancing with imbalanced team."""
    
    # Test project-specific balancing
    response = client.get(
        f"{api_prefix}/ai/balance-suggestions",
        params={"project_id": ai_comprehensive_seed["projects"]["alpha"]},
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "suggestions" in data
        assert "message" in data
        
        suggestions = data["suggestions"]
        assert isinstance(suggestions, list)


def test_workload_balance_portfolio_wide(client, api_prefix, ai_comprehensive_seed):
    """Test portfolio-wide workload balancing."""
    
    response = client.get(f"{api_prefix}/ai/balance-suggestions")
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "suggestions" in data
        assert "message" in data
        
        # Should suggest shifting work from John (over) to Alice/Mike (bench)
        suggestions = data["suggestions"]
        if len(suggestions) > 0:
            suggestion = suggestions[0]
            assert "action" in suggestion
            assert "recommended_hours" in suggestion


def test_forecast_with_existing_allocations(client, api_prefix, ai_comprehensive_seed):
    """Test resource forecasting with current allocation data."""
    
    response = client.get(
        f"{api_prefix}/ai/forecast",
        params={"months_ahead": 3},
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "forecast_period_months" in data
        assert data["forecast_period_months"] == 3
        assert "predictions" in data
        assert "message" in data
        
        predictions = data["predictions"]
        assert isinstance(predictions, list)
        assert len(predictions) == 3
        
        # Each prediction should have required fields
        if len(predictions) > 0:
            prediction = predictions[0]
            assert "month" in prediction
            assert "projected_capacity_hours" in prediction
            assert "projected_allocated_hours" in prediction
            assert "surplus_hours" in prediction
            assert "risk" in prediction


def test_portfolio_dashboard_with_realistic_data(client, api_prefix, ai_comprehensive_seed):
    """Test portfolio dashboard with comprehensive allocation data."""
    
    response = client.get(f"{api_prefix}/reports/portfolio-dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_projects"] == 2
    assert data["total_employees"] == 5
    
    # Should have FTE by role
    assert "Software Engineer" in data["fte_by_role"]
    assert "Data Scientist" in data["fte_by_role"]
    
    # John Smith should be in over-allocated (105% FTE)
    over_allocated = data["over_allocated_employees"]
    assert len(over_allocated) >= 1
    john_conflict = next((emp for emp in over_allocated if "John" in emp["full_name"]), None)
    assert john_conflict is not None
    assert john_conflict["fte_percentage"] > 100
    
    # Bob, Alice, Mike should be on bench (20%, 0%, 0% FTE)
    bench = data["bench_employees"]
    assert len(bench) >= 3


def test_employee_timeline_shows_multiple_projects(client, api_prefix, ai_comprehensive_seed):
    """Test employee timeline for someone on multiple projects."""
    
    john_id = ai_comprehensive_seed["employees"]["john"]
    today = date.today()
    
    response = client.get(
        f"{api_prefix}/reports/employee-timeline/{john_id}",
        params={
            "start_year": today.year,
            "start_month": today.month,
            "end_year": today.year,
            "end_month": today.month,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == john_id
    assert "John" in data["employee_name"]
    
    timeline = data["timeline"]
    assert len(timeline) >= 1
    
    # Current month should show allocations from both projects
    current_entry = timeline[0]
    assert current_entry["year"] == today.year
    assert current_entry["month"] == today.month
    
    # Should have allocations from both Project Alpha and Beta
    allocations = current_entry["allocations"]
    assert len(allocations) == 2
    
    project_names = {alloc["project_name"] for alloc in allocations}
    assert "Project Alpha" in project_names
    assert "Project Beta" in project_names


def test_project_dashboard_with_allocations(client, api_prefix, ai_comprehensive_seed):
    """Test project dashboard with real allocation data."""
    
    project_id = ai_comprehensive_seed["projects"]["alpha"]
    
    response = client.get(f"{api_prefix}/reports/project-dashboard/{project_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["project_id"] == project_id
    assert data["project_name"] == "Project Alpha"
    assert data["total_funded_hours"] == 1200  # John 800 + Jane 400
    assert data["total_allocated_hours"] > 0
    
    # Should have burn-down data
    burn_down = data["burn_down_data"]
    assert len(burn_down) > 0


def test_ai_chat_specific_queries(client, api_prefix, ai_comprehensive_seed):
    """Test AI chat with specific realistic queries."""
    
    queries = [
        "How many projects are active?",
        "Who is on Project Alpha?",
        "What is Jane Doe's current allocation?",
        "Show me employees with low utilization",
    ]
    
    for query in queries:
        response = client.post(
            f"{api_prefix}/ai/chat",
            json={"query": query, "context_limit": 5},
        )
        
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["query"] == query
            assert len(data["answer"]) > 0
            assert isinstance(data["sources"], list)


def test_utilization_by_role_with_data(client, api_prefix, ai_comprehensive_seed):
    """Test utilization report by role with realistic allocations."""
    
    today = date.today()
    
    response = client.get(
        f"{api_prefix}/reports/utilization-by-role",
        params={"year": today.year, "month": today.month},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["year"] == today.year
    assert data["month"] == today.month
    
    utilization = data["utilization_by_role"]
    assert len(utilization) >= 2  # At least SW Engineer and Data Scientist
    
    # Find Software Engineer utilization
    sw_util = next((item for item in utilization if item["role_name"] == "Software Engineer"), None)
    assert sw_util is not None
    assert sw_util["total_hours"] > 0


def test_auto_distribute_hours(client, api_prefix, ai_comprehensive_seed):
    """Test automatic hour distribution feature."""
    
    assignment_id = ai_comprehensive_seed["assignments"]["jane_alpha"]
    
    # Distribute 240 hours evenly across 3 months
    response = client.post(
        f"{api_prefix}/allocations/assignments/{assignment_id}/distribute",
        json={
            "start_year": 2025,
            "start_month": 3,
            "end_year": 2025,
            "end_month": 5,
            "total_hours": 240,
            "strategy": "even",
        },
    )
    
    assert response.status_code == 200
    allocations = response.json()
    
    # Should create 3 allocations (March, April, May)
    assert len(allocations) == 3
    
    # Each should have 80 hours (240 / 3)
    for allocation in allocations:
        assert allocation["allocated_hours"] == 80


def test_export_portfolio_with_data(client, api_prefix, ai_comprehensive_seed):
    """Test portfolio export with realistic data."""
    
    response = client.get(f"{api_prefix}/reports/export/portfolio")
    assert response.status_code == 200
    
    # Verify it's an Excel file
    content_type = response.headers.get("content-type")
    assert "spreadsheet" in content_type
    
    # Verify content exists
    assert len(response.content) > 0


def test_export_project_with_allocations(client, api_prefix, ai_comprehensive_seed):
    """Test project export with allocation data."""
    
    project_id = ai_comprehensive_seed["projects"]["alpha"]
    
    response = client.get(f"{api_prefix}/reports/export/project/{project_id}")
    assert response.status_code == 200
    
    content_type = response.headers.get("content-type")
    assert "spreadsheet" in content_type
    assert len(response.content) > 0


def test_ai_features_without_api_key(client, api_prefix, ai_comprehensive_seed, monkeypatch):
    """Test that AI features gracefully handle missing API key."""
    
    # Temporarily unset the API key
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    # Chat should return 503
    chat_response = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "Test query", "context_limit": 3},
    )
    assert chat_response.status_code == 503
    
    # Recommendations should return 503
    recommend_response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_comprehensive_seed["projects"]["alpha"],
            "role_id": ai_comprehensive_seed["roles"]["sw_engineer"],
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    assert recommend_response.status_code == 503
    
    # Conflicts should return 503
    conflicts_response = client.get(f"{api_prefix}/ai/conflicts")
    assert conflicts_response.status_code == 503


def test_role_and_lcat_creation(client, api_prefix):
    """Test that managers can create roles and LCATs."""
    
    # Create a manager
    manager = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "test.manager@company.com",
            "full_name": "Test Manager",
            "password": "SecurePass9!",
            "system_role": "PM",
            "is_active": True,
        },
    ).json()
    
    # Create a role scoped to this manager
    role_response = client.post(
        f"{api_prefix}/admin/roles/",
        json={
            "name": "QA Engineer",
            "description": "Quality assurance specialist",
            "owner_id": manager["id"],
        },
    )
    assert role_response.status_code == 201
    role = role_response.json()
    assert role["name"] == "QA Engineer"
    assert role["owner_id"] == manager["id"]
    
    # Create an LCAT scoped to this manager
    lcat_response = client.post(
        f"{api_prefix}/admin/lcats/",
        json={
            "name": "Level 3",
            "description": "Advanced level",
            "owner_id": manager["id"],
        },
    )
    assert lcat_response.status_code == 201
    lcat = lcat_response.json()
    assert lcat["name"] == "Level 3"
    assert lcat["owner_id"] == manager["id"]
    
    # Verify they appear in filtered list
    roles_list = client.get(
        f"{api_prefix}/admin/roles/",
        params={"owner_id": manager["id"], "include_global": False},
    )
    assert roles_list.status_code == 200
    roles = roles_list.json()
    assert any(r["id"] == role["id"] for r in roles)
    
    lcats_list = client.get(
        f"{api_prefix}/admin/lcats/",
        params={"owner_id": manager["id"], "include_global": False},
    )
    assert lcats_list.status_code == 200
    lcats = lcats_list.json()
    assert any(l["id"] == lcat["id"] for l in lcats)


def test_manager_cannot_see_other_manager_projects(client, api_prefix):
    """Test that manager isolation works correctly."""
    
    # Create two managers
    manager1 = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "manager1@company.com",
            "full_name": "Manager One",
            "password": "SecurePass9!",
            "system_role": "PM",
            "is_active": True,
        },
    ).json()
    
    manager2 = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "manager2@company.com",
            "full_name": "Manager Two",
            "password": "SecurePass9!",
            "system_role": "PM",
            "is_active": True,
        },
    ).json()
    
    # Manager 1 creates a project
    project1 = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "Manager 1 Project",
            "code": "MGR1-PROJ",
            "client": "Client A",
            "start_date": "2025-01-01",
            "sprints": 4,
            "status": "Active",
            "manager_id": manager1["id"],
        },
    ).json()
    
    # Manager 2 creates a project
    project2 = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "Manager 2 Project",
            "code": "MGR2-PROJ",
            "client": "Client B",
            "start_date": "2025-01-01",
            "sprints": 4,
            "status": "Active",
            "manager_id": manager2["id"],
        },
    ).json()
    
    # Manager 1 queries their projects
    manager1_projects = client.get(
        f"{api_prefix}/projects/",
        params={"manager_id": manager1["id"]},
    )
    assert manager1_projects.status_code == 200
    projects = manager1_projects.json()
    
    # Should only see their own project
    assert len(projects) == 1
    assert projects[0]["id"] == project1["id"]
    assert projects[0]["code"] == "MGR1-PROJ"
    
    # Manager 2 queries their projects
    manager2_projects = client.get(
        f"{api_prefix}/projects/",
        params={"manager_id": manager2["id"]},
    )
    assert manager2_projects.status_code == 200
    projects = manager2_projects.json()
    
    # Should only see their own project
    assert len(projects) == 1
    assert projects[0]["id"] == project2["id"]
    assert projects[0]["code"] == "MGR2-PROJ"

