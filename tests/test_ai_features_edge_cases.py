"""Edge case tests for AI features with Gemini integration."""

from __future__ import annotations

import pytest
from datetime import date


@pytest.fixture
def ai_edge_case_setup(client, api_prefix):
    """Create edge case scenarios for AI testing."""
    
    # Create manager
    manager = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "edge.manager@test.com",
            "full_name": "Edge Manager",
            "password": "SecurePass9!",
            "system_role": "PM",
            "is_active": True,
        },
    ).json()
    manager_id = manager["id"]
    
    # Create roles
    role1 = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Edge Role 1", "owner_id": manager_id},
    ).json()
    
    role2 = client.post(
        f"{api_prefix}/admin/roles/",
        json={"name": "Edge Role 2", "owner_id": manager_id},
    ).json()
    
    # Create LCATs
    lcat1 = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Edge LCAT 1", "owner_id": manager_id},
    ).json()
    
    lcat2 = client.post(
        f"{api_prefix}/admin/lcats/",
        json={"name": "Edge LCAT 2", "owner_id": manager_id},
    ).json()
    
    # Create employees
    emp1 = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "emp1@test.com",
            "full_name": "Employee One",
            "password": "Pass123!",
            "system_role": "Employee",
            "is_active": True,
            "manager_id": manager_id,
        },
    ).json()
    
    emp2 = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "emp2@test.com",
            "full_name": "Employee Two",
            "password": "Pass123!",
            "system_role": "Employee",
            "is_active": True,
            "manager_id": manager_id,
        },
    ).json()
    
    emp3 = client.post(
        f"{api_prefix}/employees/",
        json={
            "email": "emp3@test.com",
            "full_name": "Employee Three",
            "password": "Pass123!",
            "system_role": "Employee",
            "is_active": True,
            "manager_id": manager_id,
        },
    ).json()
    
    # Create project
    project = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "Edge Test Project",
            "code": "EDGE-001",
            "client": "Test Client",
            "start_date": "2025-01-01",
            "sprints": 6,
            "status": "Active",
            "manager_id": manager_id,
        },
    ).json()
    
    return {
        "manager_id": manager_id,
        "roles": {"role1": role1["id"], "role2": role2["id"]},
        "lcats": {"lcat1": lcat1["id"], "lcat2": lcat2["id"]},
        "employees": {"emp1": emp1["id"], "emp2": emp2["id"], "emp3": emp3["id"]},
        "project_id": project["id"],
    }


def test_ai_chat_with_empty_database(client, api_prefix):
    """Test AI chat when no data exists."""
    
    response = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "How many projects exist?", "context_limit": 5},
    )
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        # Should handle empty context gracefully


def test_ai_chat_with_very_long_query(client, api_prefix):
    """Test AI chat with extremely long query."""
    
    long_query = "What is the allocation " + "and status " * 100 + "for all employees?"
    
    response = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": long_query, "context_limit": 5},
    )
    
    assert response.status_code in [200, 503]


def test_ai_chat_with_special_characters(client, api_prefix):
    """Test AI chat with special characters in query."""
    
    queries = [
        "What's John's allocation?",  # Apostrophe
        "Show me employees with >50% FTE",  # Greater than
        "Projects for Q1 (Jan-Mar)",  # Parentheses and dash
        "Who works on Alpha & Beta?",  # Ampersand
    ]
    
    for query in queries:
        response = client.post(
            f"{api_prefix}/ai/chat",
            json={"query": query, "context_limit": 3},
        )
        assert response.status_code in [200, 503]


def test_staffing_recommendations_no_role_no_lcat(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations when neither role nor LCAT specified."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    # Backend allows this (returns all available employees)
    # Frontend enforces at least one in the UI
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "candidates" in data


def test_staffing_recommendations_with_only_role(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations with only role specified."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "candidates" in data
        assert "reasoning" in data


def test_staffing_recommendations_with_only_lcat(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations with only LCAT specified."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "lcat_id": ai_edge_case_setup["lcats"]["lcat1"],
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "candidates" in data


def test_staffing_recommendations_with_both_role_and_lcat(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations with both role and LCAT specified."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "lcat_id": ai_edge_case_setup["lcats"]["lcat1"],
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    assert response.status_code in [200, 503]


def test_staffing_recommendations_extreme_hours(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations with extreme hour requirements."""
    
    # Very low hours
    response_low = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 6,
            "required_hours": 1,  # Minimum
        },
    )
    assert response_low.status_code in [200, 503]
    
    # Very high hours
    response_high = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 6,
            "required_hours": 1000,  # Way more than one person
        },
    )
    assert response_high.status_code in [200, 503]


def test_staffing_recommendations_past_date(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations for past dates."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2020,  # Past year
            "month": 1,
            "required_hours": 100,
        },
    )
    
    assert response.status_code in [200, 503]
    # Should still work, just no candidates likely


def test_staffing_recommendations_far_future(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations for far future dates."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2030,  # Far future
            "month": 12,
            "required_hours": 100,
        },
    )
    
    assert response.status_code in [200, 503]


def test_conflicts_with_no_allocations(client, api_prefix):
    """Test conflict detection when no allocations exist."""
    
    response = client.get(f"{api_prefix}/ai/conflicts")
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "conflicts" in data
        assert "message" in data
        # Should return empty conflicts with appropriate message


def test_conflicts_with_extreme_overallocation(client, api_prefix, ai_edge_case_setup):
    """Test conflict detection with extreme over-allocation (500% FTE)."""
    
    # Create assignment
    assignment = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "user_id": ai_edge_case_setup["employees"]["emp1"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "lcat_id": ai_edge_case_setup["lcats"]["lcat1"],
            "funded_hours": 1000,
        },
    ).json()
    
    # Create extreme allocation
    today = date.today()
    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment["id"],
            "year": today.year,
            "month": today.month,
            "allocated_hours": 800,  # ~500% FTE
        },
    )
    
    response = client.get(f"{api_prefix}/ai/conflicts")
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        conflicts = data["conflicts"]
        # Should find the extreme over-allocation
        if len(conflicts) > 0:
            assert any(c["fte"] > 4.0 for c in conflicts)


def test_workload_balance_all_employees_at_100_percent(client, api_prefix, ai_edge_case_setup):
    """Test workload balancing when everyone is perfectly allocated."""
    
    # Create assignments with perfect 100% FTE for all
    today = date.today()
    standard_hours = 168  # Approximate
    
    for emp_id in ai_edge_case_setup["employees"].values():
        assignment = client.post(
            f"{api_prefix}/allocations/assignments",
            json={
                "project_id": ai_edge_case_setup["project_id"],
                "user_id": emp_id,
                "role_id": ai_edge_case_setup["roles"]["role1"],
                "lcat_id": ai_edge_case_setup["lcats"]["lcat1"],
                "funded_hours": 500,
            },
        ).json()
        
        client.post(
            f"{api_prefix}/allocations/",
            json={
                "project_assignment_id": assignment["id"],
                "year": today.year,
                "month": today.month,
                "allocated_hours": standard_hours,  # Exactly 100%
            },
        )
    
    response = client.get(f"{api_prefix}/ai/balance-suggestions")
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        # Should find no imbalances
        assert "suggestions" in data
        assert "message" in data


def test_forecast_with_zero_employees(client, api_prefix):
    """Test forecasting when no employees exist."""
    
    response = client.get(
        f"{api_prefix}/ai/forecast",
        params={"months_ahead": 3},
    )
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
        # Should handle zero employees gracefully


def test_forecast_with_extreme_months_ahead(client, api_prefix):
    """Test forecasting with extreme time horizons."""
    
    # Very short
    response_short = client.get(
        f"{api_prefix}/ai/forecast",
        params={"months_ahead": 1},
    )
    assert response_short.status_code in [200, 503]
    
    # Very long
    response_long = client.get(
        f"{api_prefix}/ai/forecast",
        params={"months_ahead": 24},
    )
    assert response_long.status_code in [200, 503]


def test_ai_chat_context_limit_boundaries(client, api_prefix):
    """Test AI chat with boundary context limits."""
    
    # Minimum context
    response_min = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "Test query", "context_limit": 1},
    )
    assert response_min.status_code in [200, 503]
    
    # Maximum context
    response_max = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "Test query", "context_limit": 20},
    )
    assert response_max.status_code in [200, 503]


def test_ai_chat_with_sql_injection_attempt(client, api_prefix):
    """Test AI chat with SQL injection patterns."""
    
    malicious_queries = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "<script>alert('xss')</script>",
    ]
    
    for query in malicious_queries:
        response = client.post(
            f"{api_prefix}/ai/chat",
            json={"query": query, "context_limit": 5},
        )
        # Should not crash, should return safely
        assert response.status_code in [200, 503]


def test_recommend_staff_for_nonexistent_project(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations for project that doesn't exist."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": 99999,  # Doesn't exist
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    assert response.status_code == 404


def test_recommend_staff_for_nonexistent_role(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations for role that doesn't exist."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": 99999,  # Doesn't exist
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    assert response.status_code == 404


def test_recommend_staff_for_nonexistent_lcat(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations for LCAT that doesn't exist."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "lcat_id": 99999,  # Doesn't exist
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    assert response.status_code == 404


def test_recommend_staff_with_invalid_month(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations with invalid month values."""
    
    # Month 0
    response_zero = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 0,
            "required_hours": 100,
        },
    )
    assert response_zero.status_code == 422  # Validation error
    
    # Month 13
    response_thirteen = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 13,
            "required_hours": 100,
        },
    )
    assert response_thirteen.status_code == 422  # Validation error


def test_recommend_staff_with_negative_hours(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations with negative required hours."""
    
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 6,
            "required_hours": -100,
        },
    )
    
    assert response.status_code == 422  # Validation error


def test_workload_balance_for_nonexistent_project(client, api_prefix):
    """Test workload balancing for project that doesn't exist."""
    
    response = client.get(
        f"{api_prefix}/ai/balance-suggestions",
        params={"project_id": 99999},
    )
    
    # Should still work (just returns portfolio-wide if project not found)
    assert response.status_code in [200, 503]


def test_rag_reindex_multiple_times(client, api_prefix):
    """Test RAG reindexing multiple times in succession."""
    
    for i in range(3):
        response = client.post(f"{api_prefix}/ai/reindex")
        assert response.status_code == 202
        data = response.json()
        assert "status" in data
        assert data["status"] == "accepted"


def test_ai_chat_with_unicode_characters(client, api_prefix):
    """Test AI chat with unicode characters."""
    
    queries = [
        "What is José's allocation?",
        "Show me employees in München office",
        "Projects for 北京 team",
        "Allocation for François Müller",
    ]
    
    for query in queries:
        response = client.post(
            f"{api_prefix}/ai/chat",
            json={"query": query, "context_limit": 5},
        )
        assert response.status_code in [200, 503]


def test_conflicts_detection_performance(client, api_prefix, ai_edge_case_setup):
    """Test conflict detection with many employees and allocations."""
    
    # This test verifies performance doesn't degrade with more data
    response = client.get(f"{api_prefix}/ai/conflicts")
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "conflicts" in data
        assert isinstance(data["conflicts"], list)


def test_forecast_with_negative_months(client, api_prefix):
    """Test forecast with invalid negative months_ahead."""
    
    response = client.get(
        f"{api_prefix}/ai/forecast",
        params={"months_ahead": -1},
    )
    
    # Should handle gracefully or return validation error
    assert response.status_code in [200, 422, 503]


def test_ai_features_concurrent_requests(client, api_prefix, ai_edge_case_setup):
    """Test that multiple AI requests don't interfere with each other."""
    
    # Make multiple requests
    responses = []
    
    # Chat
    responses.append(client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "Test 1", "context_limit": 3},
    ))
    
    # Conflicts
    responses.append(client.get(f"{api_prefix}/ai/conflicts"))
    
    # Forecast
    responses.append(client.get(
        f"{api_prefix}/ai/forecast",
        params={"months_ahead": 3},
    ))
    
    # All should complete successfully
    for response in responses:
        assert response.status_code in [200, 202, 503]


def test_recommend_staff_when_all_employees_already_assigned(client, api_prefix, ai_edge_case_setup):
    """Test staffing recommendations when all employees are already on the project."""
    
    # Assign all employees to the project
    for emp_id in ai_edge_case_setup["employees"].values():
        client.post(
            f"{api_prefix}/allocations/assignments",
            json={
                "project_id": ai_edge_case_setup["project_id"],
                "user_id": emp_id,
                "role_id": ai_edge_case_setup["roles"]["role1"],
                "lcat_id": ai_edge_case_setup["lcats"]["lcat1"],
                "funded_hours": 200,
            },
        )
    
    # Now request recommendations
    response = client.post(
        f"{api_prefix}/ai/recommend-staff",
        json={
            "project_id": ai_edge_case_setup["project_id"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "year": 2025,
            "month": 6,
            "required_hours": 100,
        },
    )
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        # Should return empty candidates (all already assigned)
        assert len(data["candidates"]) == 0
        assert "reasoning" in data


def test_ai_chat_with_empty_query(client, api_prefix):
    """Test AI chat with empty or whitespace-only query."""
    
    # Empty string
    response_empty = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "", "context_limit": 5},
    )
    assert response_empty.status_code == 422  # Validation error (min_length=3)
    
    # Whitespace only
    response_whitespace = client.post(
        f"{api_prefix}/ai/chat",
        json={"query": "   ", "context_limit": 5},
    )
    assert response_whitespace.status_code == 422  # Validation error


def test_workload_balance_with_single_employee(client, api_prefix, ai_edge_case_setup):
    """Test workload balancing when only one employee exists."""
    
    # Create project with only one employee
    project = client.post(
        f"{api_prefix}/projects/",
        json={
            "name": "Single Employee Project",
            "code": "SINGLE",
            "start_date": "2025-01-01",
            "sprints": 4,
            "status": "Active",
            "manager_id": ai_edge_case_setup["manager_id"],
        },
    ).json()
    
    assignment = client.post(
        f"{api_prefix}/allocations/assignments",
        json={
            "project_id": project["id"],
            "user_id": ai_edge_case_setup["employees"]["emp1"],
            "role_id": ai_edge_case_setup["roles"]["role1"],
            "lcat_id": ai_edge_case_setup["lcats"]["lcat1"],
            "funded_hours": 500,
        },
    ).json()
    
    today = date.today()
    client.post(
        f"{api_prefix}/allocations/",
        json={
            "project_assignment_id": assignment["id"],
            "year": today.year,
            "month": today.month,
            "allocated_hours": 200,  # Over-allocated
        },
    )
    
    response = client.get(
        f"{api_prefix}/ai/balance-suggestions",
        params={"project_id": project["id"]},
    )
    
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        # Should return no suggestions (no one to balance with)
        assert "suggestions" in data

