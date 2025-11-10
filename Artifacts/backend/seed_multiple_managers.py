"""
Comprehensive seed script for multiple managers with rich test data.

This script:
1. Wipes the existing database clean
2. Creates 3 manager accounts
3. For each manager, creates:
   - 8-10 employees
   - 4-5 roles
   - 4-5 LCATs
   - 5-7 projects with assignments
   - Rich allocation data spanning 18 months
4. Ensures complete data isolation between managers
"""
import sys
from datetime import date, timedelta
from pathlib import Path
import random
import os

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.session import SessionLocal, engine, create_db_and_tables
from app.models import Base, SystemRole
from app import crud, schemas
from app.core import security
from app.core.config import settings

# Seed data templates
MANAGER_DATA = [
    {
        "email": "sarah.martinez@staffalloc.com",
        "full_name": "Sarah Martinez",
        "password": "manager123"
    },
    {
        "email": "james.wilson@staffalloc.com",
        "full_name": "James Wilson",
        "password": "manager123"
    },
    {
        "email": "aisha.patel@staffalloc.com",
        "full_name": "Aisha Patel",
        "password": "manager123"
    }
]

EMPLOYEE_NAMES = [
    "Alex Johnson", "Taylor Smith", "Jordan Lee", "Morgan Brown",
    "Casey Davis", "Riley Garcia", "Avery Martinez", "Quinn Anderson",
    "Blake Thompson", "Cameron White", "Dakota Harris", "Emerson Clark",
    "Finley Lewis", "Harper Robinson", "Indigo Walker", "Jamie Hall"
]

ROLES_DATA = [
    {"name": "Software Engineer", "description": "Develops and maintains software systems"},
    {"name": "Data Scientist", "description": "Analyzes data and builds ML models"},
    {"name": "DevOps Engineer", "description": "Manages infrastructure and deployments"},
    {"name": "QA Engineer", "description": "Ensures quality through testing"},
    {"name": "Product Manager", "description": "Manages product roadmap and requirements"},
    {"name": "UI/UX Designer", "description": "Designs user interfaces and experiences"},
    {"name": "Cyber Analyst", "description": "Monitors and protects information systems"},
]

LCATS_DATA = [
    {"name": "Junior", "description": "0-2 years experience"},
    {"name": "Mid-level", "description": "2-5 years experience"},
    {"name": "Senior", "description": "5-10 years experience"},
    {"name": "Principal", "description": "10+ years experience"},
    {"name": "Lead", "description": "Team lead with 7+ years experience"},
]

PROJECT_TEMPLATES = [
    {"name": "Customer Portal Redesign", "client": "Acme Corp", "sprints": 12},
    {"name": "Mobile App Development", "client": "TechStart Inc", "sprints": 16},
    {"name": "Data Migration Project", "client": "Global Finance", "sprints": 8},
    {"name": "API Integration Platform", "client": "CloudSys", "sprints": 14},
    {"name": "Security Audit System", "client": "SecureNet", "sprints": 10},
    {"name": "Analytics Dashboard", "client": "DataCorp", "sprints": 12},
    {"name": "Cloud Infrastructure Upgrade", "client": "MegaTech", "sprints": 18},
]


def wipe_database():
    """Delete database files and recreate schema."""
    print("🗑️  Wiping database...")
    
    # Get database file path from settings
    db_path = Path(settings.SQLITE_DB_PATH)
    
    # Delete database files if they exist
    for file_suffix in ['', '-shm', '-wal']:
        file_path = Path(str(db_path) + file_suffix)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  Deleted {file_path.name}")
            except Exception as e:
                print(f"  Warning: Could not delete {file_path.name}: {e}")
    
    # Recreate database
    create_db_and_tables()
    print("✓ Database wiped and recreated")


def create_manager(db: SessionLocal, manager_info: dict) -> int:
    """Create a manager (PM) account."""
    password_hash = security.get_password_hash(manager_info["password"])
    
    manager = crud.create_user(
        db,
        schemas.UserCreate(
            email=manager_info["email"],
            full_name=manager_info["full_name"],
            system_role=SystemRole.PM,
            is_active=True,
            password=manager_info["password"]
        ),
        password_hash=password_hash
    )
    
    print(f"  ✓ Created manager: {manager.full_name} (ID: {manager.id})")
    return manager.id


def create_roles_for_manager(db: SessionLocal, manager_id: int) -> list[int]:
    """Create roles for a manager."""
    role_ids = []
    num_roles = random.randint(4, 5)
    selected_roles = random.sample(ROLES_DATA, num_roles)
    
    for role_data in selected_roles:
        try:
            role = crud.create_role(
                db,
                schemas.RoleCreate(
                    name=role_data["name"],
                    description=role_data["description"],
                    owner_id=manager_id
                ),
                owner_id=manager_id
            )
            role_ids.append(role.id)
        except Exception as e:
            print(f"      Error creating role {role_data['name']}: {e}")
            continue
    
    print(f"    ✓ Created {len(role_ids)} roles")
    return role_ids


def create_lcats_for_manager(db: SessionLocal, manager_id: int) -> list[int]:
    """Create LCATs for a manager."""
    lcat_ids = []
    num_lcats = random.randint(4, 5)
    selected_lcats = random.sample(LCATS_DATA, num_lcats)
    
    for lcat_data in selected_lcats:
        try:
            lcat = crud.create_lcat(
                db,
                schemas.LCATCreate(
                    name=lcat_data["name"],
                    description=lcat_data["description"],
                    owner_id=manager_id
                ),
                owner_id=manager_id
            )
            lcat_ids.append(lcat.id)
        except Exception as e:
            print(f"      Error creating LCAT {lcat_data['name']}: {e}")
            continue
    
    print(f"    ✓ Created {len(lcat_ids)} LCATs")
    return lcat_ids


def create_employees_for_manager(db: SessionLocal, manager_id: int, manager_email: str) -> list[int]:
    """Create employees for a manager."""
    employee_ids = []
    num_employees = random.randint(8, 10)
    selected_names = random.sample(EMPLOYEE_NAMES, num_employees)
    
    for idx, name in enumerate(selected_names):
        # Create email from manager's domain with manager ID for uniqueness
        domain = manager_email.split('@')[1]
        first_name = name.split()[0].lower()
        last_name = name.split()[1].lower()
        email = f"{first_name}.{last_name}.m{manager_id}@{domain}"
        
        password_hash = security.get_password_hash("employee123")
        
        employee = crud.create_user(
            db,
            schemas.UserCreate(
                email=email,
                full_name=name,
                system_role=SystemRole.EMPLOYEE,
                is_active=True,
                manager_id=manager_id,
                password="employee123"
            ),
            password_hash=password_hash
        )
        employee_ids.append(employee.id)
    
    print(f"    ✓ Created {len(employee_ids)} employees")
    return employee_ids


def create_projects_with_allocations(
    db: SessionLocal,
    manager_id: int,
    employee_ids: list[int],
    role_ids: list[int],
    lcat_ids: list[int]
):
    """Create projects with assignments and rich allocation data."""
    num_projects = random.randint(5, 7)
    selected_projects = random.sample(PROJECT_TEMPLATES, num_projects)
    
    start_date = date.today() - timedelta(days=180)  # Start 6 months ago
    
    for proj_idx, proj_template in enumerate(selected_projects):
        # Create project
        project_start = start_date + timedelta(days=proj_idx * 30)
        code = f"PROJ-{manager_id}-{proj_idx+1:02d}"
        
        project = crud.create_project(
            db,
            schemas.ProjectCreate(
                name=proj_template["name"],
                code=code,
                client=proj_template["client"],
                start_date=project_start,
                sprints=proj_template["sprints"],
                manager_id=manager_id,
                status="Active"
            )
        )
        
        # Assign 3-6 employees to this project
        num_assignments = random.randint(3, 6)
        assigned_employees = random.sample(employee_ids, num_assignments)
        
        for emp_id in assigned_employees:
            role_id = random.choice(role_ids)
            lcat_id = random.choice(lcat_ids)
            funded_hours = random.randint(400, 1200)
            
            assignment = crud.create_project_assignment(
                db,
                schemas.ProjectAssignmentCreate(
                    project_id=project.id,
                    user_id=emp_id,
                    role_id=role_id,
                    lcat_id=lcat_id,
                    funded_hours=funded_hours
                )
            )
            
            # Create allocations spanning 12-18 months
            allocation_months = random.randint(12, 18)
            remaining_hours = funded_hours
            
            for month_offset in range(allocation_months):
                if remaining_hours <= 0:
                    break
                
                alloc_date = project_start + timedelta(days=month_offset * 30)
                
                # Vary allocation intensity
                if remaining_hours < 100:
                    month_hours = remaining_hours
                else:
                    max_hours = min(remaining_hours, 180)
                    min_hours = max(20, max_hours // 4)
                    month_hours = random.randint(min_hours, max_hours)
                
                if month_hours > 0:
                    crud.create_allocation(
                        db,
                        schemas.AllocationCreate(
                            project_assignment_id=assignment.id,
                            year=alloc_date.year,
                            month=alloc_date.month,
                            allocated_hours=month_hours
                        )
                    )
                    remaining_hours -= month_hours
    
    print(f"    ✓ Created {num_projects} projects with assignments and allocations")


def main():
    """Run the complete seeding process."""
    print("=" * 70)
    print("StaffAlloc: Comprehensive Multi-Manager Seed Data")
    print("=" * 70)
    print()
    
    # Wipe and recreate database
    wipe_database()
    print()
    
    db = SessionLocal()
    try:
        # Create each manager's isolated workspace
        for idx, manager_info in enumerate(MANAGER_DATA, 1):
            try:
                print(f"📊 Setting up Manager {idx}: {manager_info['full_name']}")
                
                # Create manager
                manager_id = create_manager(db, manager_info)
                
                # Create roles
                role_ids = create_roles_for_manager(db, manager_id)
                
                # Create LCATs
                lcat_ids = create_lcats_for_manager(db, manager_id)
                
                # Create employees
                employee_ids = create_employees_for_manager(db, manager_id, manager_info["email"])
                
                # Create projects with assignments and allocations
                create_projects_with_allocations(db, manager_id, employee_ids, role_ids, lcat_ids)
                
                print()
            except Exception as manager_error:
                print(f"❌ Error creating manager {manager_info['full_name']}: {manager_error}")
                import traceback
                traceback.print_exc()
                raise
        
        # Create an admin user
        print("👑 Creating admin user...")
        admin_hash = security.get_password_hash("admin123")
        crud.create_user(
            db,
            schemas.UserCreate(
                email="admin@staffalloc.com",
                full_name="System Administrator",
                system_role=SystemRole.ADMIN,
                is_active=True,
                password="admin123"
            ),
            password_hash=admin_hash
        )
        print("  ✓ Created admin account")
        print()
        
        print("=" * 70)
        print("✅ Seeding completed successfully!")
        print("=" * 70)
        print()
        print("🔐 Login Credentials:")
        print("-" * 70)
        for manager_info in MANAGER_DATA:
            print(f"  Email: {manager_info['email']}")
            print(f"  Password: {manager_info['password']}")
            print()
        print(f"  Admin Email: admin@staffalloc.com")
        print(f"  Admin Password: admin123")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

