"""Seed comprehensive project data for Sarah Martinez's account."""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import crud, models, schemas
from app.core.security import get_password_hash

def seed_data():
    """Seed comprehensive data for testing AI features."""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Seeding StaffAlloc Database with Sarah's Portfolio")
        print("=" * 60)
        
        # Check if Sarah exists
        sarah = crud.get_user_by_email(db, "sarah.martinez@company.com")
        if not sarah:
            print("\n1. Creating Sarah Martinez (PM)...")
            sarah = crud.create_user(
                db,
                schemas.UserCreate(
                    email="sarah.martinez@company.com",
                    full_name="Sarah Martinez",
                    password="SecurePass123!",
                    system_role=models.SystemRole.PM,
                    is_active=True,
                ),
                password_hash=get_password_hash("SecurePass123!"),
            )
            print(f"   ✅ Created Sarah (ID: {sarah.id})")
        else:
            print(f"\n1. Sarah Martinez already exists (ID: {sarah.id})")
        
        sarah_id = sarah.id
        
        # Create Roles
        print("\n2. Creating Roles...")
        roles = {}
        role_names = [
            ("Software Engineer", "Develops software applications"),
            ("Data Scientist", "Analyzes data and builds models"),
            ("Project Manager", "Manages projects and teams"),
            ("UX Designer", "Designs user experiences"),
            ("DevOps Engineer", "Manages infrastructure and deployments"),
            ("QA Engineer", "Tests and ensures quality"),
            ("Security Analyst", "Manages security and compliance"),
            ("Business Analyst", "Analyzes business requirements"),
        ]
        
        for name, desc in role_names:
            existing = crud.get_role_by_name(db, name, owner_id=sarah_id)
            if not existing:
                role = crud.create_role(
                    db,
                    schemas.RoleCreate(name=name, description=desc),
                    owner_id=sarah_id,
                )
                roles[name] = role
                print(f"   ✅ Created role: {name}")
            else:
                roles[name] = existing
                print(f"   ⏭️  Role exists: {name}")
        
        # Create LCATs
        print("\n3. Creating LCATs...")
        lcats = {}
        lcat_names = [
            ("Level 1", "Entry level"),
            ("Level 2", "Mid level"),
            ("Level 3", "Advanced level"),
            ("Senior", "Senior level"),
            ("Principal", "Principal level"),
            ("Lead", "Team lead level"),
        ]
        
        for name, desc in lcat_names:
            existing = crud.get_lcat_by_name(db, name, owner_id=sarah_id)
            if not existing:
                lcat = crud.create_lcat(
                    db,
                    schemas.LCATCreate(name=name, description=desc),
                    owner_id=sarah_id,
                )
                lcats[name] = lcat
                print(f"   ✅ Created LCAT: {name}")
            else:
                lcats[name] = existing
                print(f"   ⏭️  LCAT exists: {name}")
        
        # Create Employees
        print("\n4. Creating Employees...")
        employees = {}
        employee_data = [
            ("maria.garcia@company.com", "Maria Garcia"),
            ("john.smith@company.com", "John Smith"),
            ("li.wei@company.com", "Li Wei"),
            ("aisha.khan@company.com", "Aisha Khan"),
            ("carlos.rodriguez@company.com", "Carlos Rodriguez"),
            ("emily.johnson@company.com", "Emily Johnson"),
            ("raj.patel@company.com", "Raj Patel"),
            ("sophie.dubois@company.com", "Sophie Dubois"),
            ("ahmed.hassan@company.com", "Ahmed Hassan"),
            ("yuki.tanaka@company.com", "Yuki Tanaka"),
        ]
        
        for email, name in employee_data:
            existing = crud.get_user_by_email(db, email)
            if not existing:
                emp = crud.create_user(
                    db,
                    schemas.UserCreate(
                        email=email,
                        full_name=name,
                        password="Password123!",
                        system_role=models.SystemRole.EMPLOYEE,
                        is_active=True,
                        manager_id=sarah_id,
                    ),
                    password_hash=get_password_hash("Password123!"),
                )
                employees[name] = emp
                print(f"   ✅ Created employee: {name}")
            else:
                employees[name] = existing
                print(f"   ⏭️  Employee exists: {name}")
        
        # Create Projects
        print("\n5. Creating Projects...")
        projects = {}
        today = date.today()
        
        project_data = [
            ("ALPHA", "Project Alpha", "Acme Corp", today - timedelta(days=60), 8, "Active"),
            ("BETA", "Project Beta", "Tech Industries", today - timedelta(days=30), 6, "Active"),
            ("GAMMA", "Project Gamma", "Global Solutions", today, 10, "Planning"),
            ("DELTA", "Project Delta", "Innovation Labs", today + timedelta(days=30), 4, "Planning"),
        ]
        
        for code, name, client, start, sprints, status in project_data:
            existing = crud.get_project_by_code(db, code, manager_id=sarah_id)
            if not existing:
                proj = crud.create_project(
                    db,
                    schemas.ProjectCreate(
                        name=name,
                        code=code,
                        client=client,
                        start_date=start,
                        sprints=sprints,
                        status=status,
                        manager_id=sarah_id,
                    ),
                )
                projects[code] = proj
                print(f"   ✅ Created project: {name} ({code})")
            else:
                projects[code] = existing
                print(f"   ⏭️  Project exists: {name} ({code})")
        
        # Create Assignments for Project Alpha
        print("\n6. Creating Assignments for Project Alpha...")
        alpha = projects["ALPHA"]
        
        alpha_assignments = [
            ("Maria Garcia", "Project Manager", "Senior", 800),
            ("John Smith", "Software Engineer", "Senior", 600),
            ("Li Wei", "Software Engineer", "Level 3", 500),
            ("Carlos Rodriguez", "UX Designer", "Level 2", 400),
            ("Emily Johnson", "QA Engineer", "Level 2", 300),
        ]
        
        for emp_name, role_name, lcat_name, funded in alpha_assignments:
            emp = employees[emp_name]
            role = roles[role_name]
            lcat = lcats[lcat_name]
            
            existing = crud.get_assignment_by_user_and_project(db, emp.id, alpha.id)
            if not existing:
                assignment = crud.create_project_assignment(
                    db,
                    schemas.ProjectAssignmentCreate(
                        project_id=alpha.id,
                        user_id=emp.id,
                        role_id=role.id,
                        lcat_id=lcat.id,
                        funded_hours=funded,
                    ),
                )
                print(f"   ✅ Assigned {emp_name} to Alpha")
                
                # Create allocations for Maria (over-allocated scenario)
                if emp_name == "Maria Garcia":
                    # March 2025 - Heavy allocation (creates 315% FTE conflict)
                    crud.create_allocation(
                        db,
                        schemas.AllocationCreate(
                            project_assignment_id=assignment.id,
                            year=2025,
                            month=3,
                            allocated_hours=520,  # Way over standard ~168 hours
                        ),
                    )
                    print(f"      → Added Mar 2025 allocation (520h - OVER-ALLOCATED)")
                
                # Create allocations for John (normal)
                elif emp_name == "John Smith":
                    for month in range(1, 7):
                        crud.create_allocation(
                            db,
                            schemas.AllocationCreate(
                                project_assignment_id=assignment.id,
                                year=2025,
                                month=month,
                                allocated_hours=100,
                            ),
                        )
                    print(f"      → Added Jan-Jun 2025 allocations")
                
                # Create allocations for Li Wei (moderate)
                elif emp_name == "Li Wei":
                    for month in range(1, 5):
                        crud.create_allocation(
                            db,
                            schemas.AllocationCreate(
                                project_assignment_id=assignment.id,
                                year=2025,
                                month=month,
                                allocated_hours=80,
                            ),
                        )
                    print(f"      → Added Jan-Apr 2025 allocations")
            else:
                print(f"   ⏭️  {emp_name} already assigned to Alpha")
        
        # Create Assignments for Project Beta
        print("\n7. Creating Assignments for Project Beta...")
        beta = projects["BETA"]
        
        beta_assignments = [
            ("John Smith", "Software Engineer", "Senior", 400),  # Also on Alpha
            ("Aisha Khan", "Data Scientist", "Level 3", 500),
            ("Raj Patel", "DevOps Engineer", "Level 2", 350),
            ("Sophie Dubois", "Business Analyst", "Level 2", 300),
        ]
        
        for emp_name, role_name, lcat_name, funded in beta_assignments:
            emp = employees[emp_name]
            role = roles[role_name]
            lcat = lcats[lcat_name]
            
            existing = crud.get_assignment_by_user_and_project(db, emp.id, beta.id)
            if not existing:
                assignment = crud.create_project_assignment(
                    db,
                    schemas.ProjectAssignmentCreate(
                        project_id=beta.id,
                        user_id=emp.id,
                        role_id=role.id,
                        lcat_id=lcat.id,
                        funded_hours=funded,
                    ),
                )
                print(f"   ✅ Assigned {emp_name} to Beta")
                
                # Create allocations
                if emp_name == "John Smith":
                    # Also on Alpha - will create cross-project load
                    for month in range(2, 6):
                        crud.create_allocation(
                            db,
                            schemas.AllocationCreate(
                                project_assignment_id=assignment.id,
                                year=2025,
                                month=month,
                                allocated_hours=60,
                            ),
                        )
                    print(f"      → Added Feb-May 2025 allocations")
                
                elif emp_name == "Aisha Khan":
                    # Light allocation (bench scenario)
                    crud.create_allocation(
                        db,
                        schemas.AllocationCreate(
                            project_assignment_id=assignment.id,
                            year=2025,
                            month=2,
                            allocated_hours=40,  # ~24% FTE
                        ),
                    )
                    print(f"      → Added Feb 2025 allocation (light - BENCH)")
                
                elif emp_name == "Raj Patel":
                    for month in range(2, 5):
                        crud.create_allocation(
                            db,
                            schemas.AllocationCreate(
                                project_assignment_id=assignment.id,
                                year=2025,
                                month=month,
                                allocated_hours=70,
                            ),
                        )
                    print(f"      → Added Feb-Apr 2025 allocations")
            else:
                print(f"   ⏭️  {emp_name} already assigned to Beta")
        
        # Create Assignments for Project Gamma
        print("\n8. Creating Assignments for Project Gamma...")
        gamma = projects["GAMMA"]
        
        gamma_assignments = [
            ("Ahmed Hassan", "Security Analyst", "Senior", 600),
            ("Yuki Tanaka", "Software Engineer", "Level 3", 450),
            ("Emily Johnson", "QA Engineer", "Level 2", 200),  # Also on Alpha
        ]
        
        for emp_name, role_name, lcat_name, funded in gamma_assignments:
            emp = employees[emp_name]
            role = roles[role_name]
            lcat = lcats[lcat_name]
            
            existing = crud.get_assignment_by_user_and_project(db, emp.id, gamma.id)
            if not existing:
                assignment = crud.create_project_assignment(
                    db,
                    schemas.ProjectAssignmentCreate(
                        project_id=gamma.id,
                        user_id=emp.id,
                        role_id=role.id,
                        lcat_id=lcat.id,
                        funded_hours=funded,
                    ),
                )
                print(f"   ✅ Assigned {emp_name} to Gamma")
                
                # Future allocations
                if emp_name == "Ahmed Hassan":
                    for month in range(11, 13):  # Nov-Dec 2025
                        crud.create_allocation(
                            db,
                            schemas.AllocationCreate(
                                project_assignment_id=assignment.id,
                                year=2025,
                                month=month,
                                allocated_hours=100,
                            ),
                        )
                    print(f"      → Added Nov-Dec 2025 allocations")
            else:
                print(f"   ⏭️  {emp_name} already assigned to Gamma")
        
        db.commit()
        
        # Summary
        print("\n" + "=" * 60)
        print("Seeding Complete!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   Manager: Sarah Martinez (ID: {sarah_id})")
        print(f"   Roles: {len(roles)} created")
        print(f"   LCATs: {len(lcats)} created")
        print(f"   Employees: {len(employees)} created")
        print(f"   Projects: {len(projects)} created")
        print(f"\n🎯 Test Scenarios Created:")
        print(f"   ✅ Over-allocation: Maria Garcia at 315% FTE in Mar 2025")
        print(f"   ✅ Cross-project load: John Smith on Alpha + Beta")
        print(f"   ✅ Bench capacity: Aisha Khan at ~24% FTE")
        print(f"   ✅ Unallocated: Several employees with 0 allocations")
        print(f"\n🚀 Ready for AI Feature Testing!")
        print(f"\n💡 Next Steps:")
        print(f"   1. Restart backend server")
        print(f"   2. Go to AI Chat → Click 'Trigger RAG reindex'")
        print(f"   3. Try: 'What is Maria Garcia's allocation?'")
        print(f"   4. Go to Project Alpha → AI Assist → Detect conflicts")
        print(f"   5. Should find Maria's 315% FTE conflict!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

