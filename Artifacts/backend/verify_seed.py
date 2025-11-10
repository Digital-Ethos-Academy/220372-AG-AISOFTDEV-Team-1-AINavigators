"""Quick verification of seed data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models import User, Project, Role, LCAT, ProjectAssignment, Allocation, SystemRole

db = SessionLocal()

try:
    # Count records
    total_users = db.query(User).count()
    managers = db.query(User).filter(User.system_role == SystemRole.PM).count()
    employees = db.query(User).filter(User.system_role == SystemRole.EMPLOYEE).count()
    projects = db.query(Project).count()
    roles = db.query(Role).count()
    lcats = db.query(LCAT).count()
    assignments = db.query(ProjectAssignment).count()
    allocations = db.query(Allocation).count()
    
    print(f"Total Users: {total_users} (Managers: {managers}, Employees: {employees})")
    print(f"Projects: {projects}")
    print(f"Roles: {roles}")
    print(f"LCATs: {lcats}")
    print(f"Assignments: {assignments}")
    print(f"Allocations: {allocations}")
    
    # Show managers
    print("\n--- Managers ---")
    for manager in db.query(User).filter(User.system_role == SystemRole.PM).all():
        emp_count = db.query(User).filter(User.manager_id == manager.id).count()
        proj_count = db.query(Project).filter(Project.manager_id == manager.id).count()
        print(f"{manager.full_name} (ID:{manager.id}): {emp_count} employees, {proj_count} projects")
        
finally:
    db.close()

