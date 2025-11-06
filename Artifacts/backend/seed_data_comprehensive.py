"""
Comprehensive seed data script for StaffAlloc application.

This script populates the database with realistic, extensive test data that
demonstrates ALL features of the application including:
- Diverse users with different system roles
- Comprehensive roles and LCATs
- Multiple projects in various statuses
- Complex project assignments across time
- Realistic monthly allocations showing over/under allocation scenarios
- Monthly hour overrides
- AI recommendations
- Audit log entries

Run this script from the backend directory:
    python seed_data_comprehensive.py
"""
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
import random

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app import models
from app.core.security import get_password_hash

# ============================================================================
# SEED DATA - ENHANCED
# ============================================================================

ROLES = [
    {"name": "Software Engineer", "description": "Develops and maintains software applications"},
    {"name": "Senior Software Engineer", "description": "Senior-level software development with leadership responsibilities"},
    {"name": "Staff Software Engineer", "description": "Expert-level technical leadership and architecture"},
    {"name": "Engineering Manager", "description": "Manages engineering teams and delivery"},
    {"name": "Product Designer", "description": "Designs user experiences and interfaces"},
    {"name": "Senior Product Designer", "description": "Senior-level design with system thinking"},
    {"name": "Data Scientist", "description": "Analyzes data and builds ML models"},
    {"name": "Senior Data Scientist", "description": "Advanced analytics and model development"},
    {"name": "DevOps Engineer", "description": "Manages infrastructure, CI/CD, and deployments"},
    {"name": "Site Reliability Engineer", "description": "Ensures system reliability and performance"},
    {"name": "QA Engineer", "description": "Tests software and ensures quality standards"},
    {"name": "QA Lead", "description": "Leads quality assurance initiatives and teams"},
    {"name": "Tech Lead", "description": "Technical leadership for projects and teams"},
    {"name": "Frontend Developer", "description": "Specializes in UI/UX development"},
    {"name": "Backend Developer", "description": "Specializes in server-side development"},
    {"name": "Full Stack Developer", "description": "Works on both frontend and backend"},
    {"name": "Mobile Developer", "description": "Develops iOS and Android applications"},
    {"name": "Security Engineer", "description": "Focuses on application and infrastructure security"},
    {"name": "Solutions Architect", "description": "Designs high-level system architecture"},
    {"name": "Product Manager", "description": "Defines product strategy and roadmap"},
]

LCATS = [
    {"name": "Junior (L1)", "description": "Entry-level professional, 0-2 years experience"},
    {"name": "Intermediate (L2)", "description": "Mid-level professional, 2-5 years experience"},
    {"name": "Senior (L3)", "description": "Senior professional, 5-8 years experience"},
    {"name": "Staff (L4)", "description": "Staff-level expert, 8-12 years experience"},
    {"name": "Principal (L5)", "description": "Principal-level expert, 12+ years experience"},
    {"name": "Manager", "description": "People management position"},
    {"name": "Senior Manager", "description": "Senior management position"},
    {"name": "Director", "description": "Director-level leadership"},
]

# Diverse set of users with different roles
USERS = [
    # Admins and Directors
    {
        "email": "sarah.chen@staffalloc.com",
        "full_name": "Sarah Chen",
        "password": "password123",
        "system_role": "Admin",
        "is_active": True,
    },
    {
        "email": "michael.rodriguez@staffalloc.com",
        "full_name": "Michael Rodriguez",
        "password": "password123",
        "system_role": "Director",
        "is_active": True,
    },
    {
        "email": "jennifer.patel@staffalloc.com",
        "full_name": "Jennifer Patel",
        "password": "password123",
        "system_role": "Director",
        "is_active": True,
    },
    
    # Project Managers
    {
        "email": "david.kim@staffalloc.com",
        "full_name": "David Kim",
        "password": "password123",
        "system_role": "PM",
        "is_active": True,
    },
    {
        "email": "emily.johnson@staffalloc.com",
        "full_name": "Emily Johnson",
        "password": "password123",
        "system_role": "PM",
        "is_active": True,
    },
    {
        "email": "james.williams@staffalloc.com",
        "full_name": "James Williams",
        "password": "password123",
        "system_role": "PM",
        "is_active": True,
    },
    
    # Engineers - Various Levels
    {
        "email": "alex.thompson@staffalloc.com",
        "full_name": "Alex Thompson",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "maria.garcia@staffalloc.com",
        "full_name": "Maria Garcia",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "robert.brown@staffalloc.com",
        "full_name": "Robert Brown",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "lisa.anderson@staffalloc.com",
        "full_name": "Lisa Anderson",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "kevin.martinez@staffalloc.com",
        "full_name": "Kevin Martinez",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "amanda.taylor@staffalloc.com",
        "full_name": "Amanda Taylor",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "daniel.lee@staffalloc.com",
        "full_name": "Daniel Lee",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "sophia.nguyen@staffalloc.com",
        "full_name": "Sophia Nguyen",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "chris.wilson@staffalloc.com",
        "full_name": "Chris Wilson",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "jessica.moore@staffalloc.com",
        "full_name": "Jessica Moore",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "ryan.jackson@staffalloc.com",
        "full_name": "Ryan Jackson",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "nicole.white@staffalloc.com",
        "full_name": "Nicole White",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "brandon.harris@staffalloc.com",
        "full_name": "Brandon Harris",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "olivia.clark@staffalloc.com",
        "full_name": "Olivia Clark",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "jason.lewis@staffalloc.com",
        "full_name": "Jason Lewis",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "rachel.robinson@staffalloc.com",
        "full_name": "Rachel Robinson",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "matthew.walker@staffalloc.com",
        "full_name": "Matthew Walker",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "hannah.young@staffalloc.com",
        "full_name": "Hannah Young",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    {
        "email": "justin.hall@staffalloc.com",
        "full_name": "Justin Hall",
        "password": "password123",
        "system_role": "Employee",
        "is_active": True,
    },
    # One inactive user
    {
        "email": "inactive.user@staffalloc.com",
        "full_name": "Inactive User",
        "password": "password123",
        "system_role": "Employee",
        "is_active": False,
    },
]

# Projects with diverse characteristics
PROJECTS = [
    # Active Projects
    {
        "code": "ECOM-2024",
        "name": "E-Commerce Platform Modernization",
        "client": "RetailMax Inc.",
        "start_date": date.today() - timedelta(days=120),
        "sprints": 24,
        "status": "Active",
        "description": "Complete overhaul of legacy e-commerce platform"
    },
    {
        "code": "MOBILE-IOS",
        "name": "iOS Mobile App Development",
        "client": "TechCorp Solutions",
        "start_date": date.today() - timedelta(days=90),
        "sprints": 16,
        "status": "Active",
        "description": "Native iOS app for customer engagement"
    },
    {
        "code": "DATA-DASH",
        "name": "Executive Analytics Dashboard",
        "client": "FinanceHub Global",
        "start_date": date.today() - timedelta(days=60),
        "sprints": 12,
        "status": "Active",
        "description": "Real-time analytics dashboard for executives"
    },
    {
        "code": "AI-CHAT",
        "name": "AI-Powered Customer Support",
        "client": "ServiceDesk Pro",
        "start_date": date.today() - timedelta(days=45),
        "sprints": 18,
        "status": "Active",
        "description": "Intelligent chatbot with NLP capabilities"
    },
    {
        "code": "LEGACY-MIG",
        "name": "Legacy System Migration",
        "client": "BankCorp International",
        "start_date": date.today() - timedelta(days=150),
        "sprints": 32,
        "status": "Active",
        "description": "Migration from mainframe to cloud architecture"
    },
    {
        "code": "HEALTH-APP",
        "name": "Healthcare Patient Portal",
        "client": "MediCare Systems",
        "start_date": date.today() - timedelta(days=30),
        "sprints": 20,
        "status": "Active",
        "description": "Secure patient portal with telemedicine features"
    },
    
    # Planning Projects
    {
        "code": "CLOUD-INFRA",
        "name": "Cloud Infrastructure Upgrade",
        "client": "DataCenter Corp",
        "start_date": date.today() + timedelta(days=14),
        "sprints": 10,
        "status": "Planning",
        "description": "Kubernetes-based infrastructure modernization"
    },
    {
        "code": "RETAIL-POS",
        "name": "Point of Sale System",
        "client": "ShopMart Retail",
        "start_date": date.today() + timedelta(days=30),
        "sprints": 14,
        "status": "Planning",
        "description": "Modern cloud-based POS system"
    },
    {
        "code": "IOT-PLATFORM",
        "name": "IoT Device Management Platform",
        "client": "SmartHome Industries",
        "start_date": date.today() + timedelta(days=45),
        "sprints": 16,
        "status": "Planning",
        "description": "Platform for managing IoT devices at scale"
    },
    
    # On Hold Project
    {
        "code": "BLOCKCHAIN",
        "name": "Blockchain Supply Chain",
        "client": "LogisticsCo",
        "start_date": date.today() - timedelta(days=80),
        "sprints": 20,
        "status": "On Hold",
        "description": "Blockchain-based supply chain tracking"
    },
    
    # Closed Project
    {
        "code": "WEB-REDESIGN",
        "name": "Corporate Website Redesign",
        "client": "BrandCompany LLC",
        "start_date": date.today() - timedelta(days=200),
        "sprints": 8,
        "status": "Closed",
        "description": "Complete redesign of corporate website"
    },
]


# ============================================================================
# SEED FUNCTIONS - ENHANCED
# ============================================================================

def seed_roles(db):
    """Seed roles table"""
    print("Seeding roles...")
    created = 0
    for role_data in ROLES:
        existing = db.query(models.Role).filter_by(name=role_data["name"]).first()
        if not existing:
            role = models.Role(**role_data)
            db.add(role)
            created += 1
    db.commit()
    print(f"✅ Created {created} roles (skipped {len(ROLES) - created} existing)")


def seed_lcats(db):
    """Seed LCATs table"""
    print("Seeding LCATs...")
    created = 0
    for lcat_data in LCATS:
        existing = db.query(models.LCAT).filter_by(name=lcat_data["name"]).first()
        if not existing:
            lcat = models.LCAT(**lcat_data)
            db.add(lcat)
            created += 1
    db.commit()
    print(f"✅ Created {created} LCATs (skipped {len(LCATS) - created} existing)")


def seed_users(db):
    """Seed users table"""
    print("Seeding users...")
    created = 0

    # Ensure admin user exists
    admin = db.query(models.User).filter_by(email="admin@staffalloc.com").first()
    if not admin:
        admin = models.User(
            email="admin@staffalloc.com",
            full_name="Admin User",
            password_hash=get_password_hash("admin123"),
            system_role="Admin",
            is_active=True,
        )
        db.add(admin)
        created += 1

    for user_data in USERS:
        existing = db.query(models.User).filter_by(email=user_data["email"]).first()
        if not existing:
            # Hash the password
            password = user_data.pop("password")
            user_data["password_hash"] = get_password_hash(password)

            user = models.User(**user_data)
            db.add(user)
            created += 1

    db.commit()
    print(f"✅ Created {created} users (skipped existing)")


def seed_projects(db):
    """Seed projects table"""
    print("Seeding projects...")
    created = 0

    # Get PMs for assignment
    pms = db.query(models.User).filter(models.User.system_role == "PM").all()
    if not pms:
        print("⚠️  No PMs found, using admin as fallback")
        pms = [db.query(models.User).filter_by(email="admin@staffalloc.com").first()]

    for idx, project_data in enumerate(PROJECTS):
        existing = db.query(models.Project).filter_by(
            code=project_data["code"]
        ).first()
        if not existing:
            # Rotate through PMs
            pm = pms[idx % len(pms)]
            project_data["manager_id"] = pm.id
            
            # Remove description as it's not in the model
            project_data.pop("description", None)
            
            project = models.Project(**project_data)
            db.add(project)
            created += 1

    db.commit()
    print(f"✅ Created {created} projects (skipped {len(PROJECTS) - created} existing)")


def seed_assignments_and_allocations(db):
    """Seed project assignments and allocations with realistic patterns"""
    print("Seeding project assignments and allocations...")

    projects = db.query(models.Project).all()
    employees = db.query(models.User).filter(
        models.User.system_role == "Employee",
        models.User.is_active == True
    ).all()
    roles = db.query(models.Role).all()
    lcats = db.query(models.LCAT).all()

    if not employees or not roles or not lcats:
        print("⚠️  Not enough data to create assignments. Skipping...")
        return

    assignments_created = 0
    allocations_created = 0

    # Define realistic allocation patterns
    allocation_patterns = {
        "full_time": [160, 160, 160, 160],  # 100% allocation
        "part_time": [80, 80, 80, 80],      # 50% allocation
        "ramping_up": [40, 80, 120, 160],   # Gradual ramp
        "ramping_down": [160, 120, 80, 40], # Gradual ramp down
        "variable": [120, 80, 160, 100],    # Variable allocation
    }

    for project in projects:
        # Determine team size based on project
        if project.status == "Planning":
            num_employees = random.randint(2, 4)
        elif project.status == "Active":
            num_employees = random.randint(5, 8)
        elif project.status == "On Hold":
            num_employees = random.randint(2, 3)
        else:  # Closed
            num_employees = random.randint(3, 5)

        # Select random employees for this project
        assigned_employees = random.sample(employees, min(num_employees, len(employees)))

        for emp in assigned_employees:
            # Check if assignment already exists
            existing = db.query(models.ProjectAssignment).filter_by(
                project_id=project.id,
                user_id=emp.id
            ).first()

            if existing:
                continue

            # Assign role and LCAT
            role = random.choice(roles)
            lcat = random.choice(lcats)
            funded_hours = random.choice([800, 1200, 1600, 2000, 2400])

            assignment = models.ProjectAssignment(
                project_id=project.id,
                user_id=emp.id,
                role_id=role.id,
                lcat_id=lcat.id,
                funded_hours=funded_hours
            )
            db.add(assignment)
            db.flush()
            assignments_created += 1

            # Create allocations based on project status
            if project.status in ["Active", "On Hold", "Closed"]:
                # Choose allocation pattern
                pattern_name = random.choice(list(allocation_patterns.keys()))
                pattern = allocation_patterns[pattern_name]

                # Calculate number of months to allocate
                if project.status == "Closed":
                    # Past project - allocations already complete
                    months_to_allocate = min(6, (project.sprints * 2) // 4)
                    start_month_offset = -180  # Start 6 months ago
                elif project.status == "On Hold":
                    # On hold - partial allocations
                    months_to_allocate = random.randint(2, 4)
                    days_since_start = (date.today() - project.start_date).days
                    start_month_offset = -days_since_start
                else:  # Active
                    # Ongoing project
                    days_since_start = (date.today() - project.start_date).days
                    months_to_allocate = min(6, max(1, days_since_start // 30))
                    start_month_offset = -days_since_start

                # Generate allocations
                allocation_date = date.today() + timedelta(days=start_month_offset)
                
                for i in range(months_to_allocate):
                    year = allocation_date.year
                    month = allocation_date.month

                    # Check if allocation already exists
                    existing_alloc = db.query(models.Allocation).filter_by(
                        project_assignment_id=assignment.id,
                        year=year,
                        month=month
                    ).first()

                    if not existing_alloc:
                        # Use pattern with some variation
                        hours = pattern[i % len(pattern)] + random.choice([-20, 0, 20])
                        hours = max(0, min(200, hours))  # Keep within reasonable bounds

                        allocation = models.Allocation(
                            project_assignment_id=assignment.id,
                            year=year,
                            month=month,
                            allocated_hours=hours
                        )
                        db.add(allocation)
                        allocations_created += 1

                    # Move to next month
                    if month == 12:
                        allocation_date = date(year + 1, 1, 1)
                    else:
                        allocation_date = date(year, month + 1, 1)

    db.commit()
    print(f"✅ Created {assignments_created} project assignments")
    print(f"✅ Created {allocations_created} allocations")


def seed_monthly_overrides(db):
    """Seed monthly hour overrides to demonstrate that feature"""
    print("Seeding monthly hour overrides...")
    created = 0

    # Get a few projects to add overrides
    projects = db.query(models.Project).filter(
        models.Project.status == "Active"
    ).limit(3).all()

    current_date = date.today()
    
    for project in projects:
        # Add override for current month (holiday month - fewer hours)
        existing = db.query(models.MonthlyHourOverride).filter_by(
            project_id=project.id,
            year=current_date.year,
            month=current_date.month
        ).first()

        if not existing:
            override = models.MonthlyHourOverride(
                project_id=project.id,
                year=current_date.year,
                month=current_date.month,
                overridden_hours=140  # Reduced from standard 160
            )
            db.add(override)
            created += 1

        # Add override for next month (extended hours)
        next_month = current_date.month + 1 if current_date.month < 12 else 1
        next_year = current_date.year if current_date.month < 12 else current_date.year + 1

        existing = db.query(models.MonthlyHourOverride).filter_by(
            project_id=project.id,
            year=next_year,
            month=next_month
        ).first()

        if not existing:
            override = models.MonthlyHourOverride(
                project_id=project.id,
                year=next_year,
                month=next_month,
                overridden_hours=176  # Extended hours
            )
            db.add(override)
            created += 1

    db.commit()
    print(f"✅ Created {created} monthly hour overrides")


def seed_ai_recommendations(db):
    """Seed AI recommendations to demonstrate that feature"""
    print("Seeding AI recommendations...")
    created = 0

    projects = db.query(models.Project).filter(
        models.Project.status.in_(["Active", "Planning"])
    ).all()

    recommendations = [
        {
            "type": "STAFFING",
            "text": "Based on project velocity, recommend adding 1 Senior Software Engineer to ECOM-2024 for Q1 2025 to meet sprint goals.",
            "context": {"project_code": "ECOM-2024", "role": "Senior Software Engineer"},
            "status": "Pending"
        },
        {
            "type": "CONFLICT_RESOLUTION",
            "text": "Employee Alex Thompson is over-allocated in December 2024 (220 hours across 2 projects). Recommend reducing allocation on DATA-DASH by 60 hours.",
            "context": {"employee": "Alex Thompson", "month": "December 2024"},
            "status": "Pending"
        },
        {
            "type": "WORKLOAD_BALANCE",
            "text": "Team workload for MOBILE-IOS shows 3 engineers at 100% capacity. Consider adding 1 mid-level engineer or adjusting sprint scope.",
            "context": {"project_code": "MOBILE-IOS"},
            "status": "Accepted"
        },
        {
            "type": "FORECAST",
            "text": "Based on current burn rate, LEGACY-MIG is projected to need 200 additional hours in Q1 2025 to stay on schedule.",
            "context": {"project_code": "LEGACY-MIG", "additional_hours": 200},
            "status": "Pending"
        },
        {
            "type": "STAFFING",
            "text": "CLOUD-INFRA (starting soon) requires 2 DevOps Engineers. Currently available: Brandon Harris, Jason Lewis (both with relevant experience).",
            "context": {"project_code": "CLOUD-INFRA", "role": "DevOps Engineer"},
            "status": "Dismissed"
        },
    ]

    for rec_data in recommendations:
        existing = db.query(models.AIRecommendation).filter_by(
            recommendation_text=rec_data["text"]
        ).first()

        if not existing:
            recommendation = models.AIRecommendation(
                recommendation_type=rec_data["type"],
                context_json=rec_data["context"],
                recommendation_text=rec_data["text"],
                status=rec_data["status"]
            )
            db.add(recommendation)
            created += 1

    db.commit()
    print(f"✅ Created {created} AI recommendations")


def seed_audit_logs(db):
    """Seed audit log entries to demonstrate activity tracking"""
    print("Seeding audit log entries...")
    created = 0

    admin = db.query(models.User).filter_by(email="admin@staffalloc.com").first()
    pm = db.query(models.User).filter(models.User.system_role == "PM").first()
    
    projects = db.query(models.Project).all()
    
    audit_entries = [
        {
            "user_id": admin.id if admin else None,
            "action": "USER_CREATE",
            "entity_type": "user",
            "entity_id": 5,
            "details": {"email": "new.employee@staffalloc.com", "role": "Employee"},
            "timestamp": datetime.now() - timedelta(days=10)
        },
        {
            "user_id": pm.id if pm else None,
            "action": "PROJECT_CREATE",
            "entity_type": "project",
            "entity_id": projects[0].id if projects else 1,
            "details": {"project_code": "ECOM-2024", "sprints": 24},
            "timestamp": datetime.now() - timedelta(days=9)
        },
        {
            "user_id": pm.id if pm else None,
            "action": "ASSIGNMENT_CREATE",
            "entity_type": "project_assignment",
            "entity_id": 1,
            "details": {"project": "ECOM-2024", "employee": "Alex Thompson", "role": "Software Engineer"},
            "timestamp": datetime.now() - timedelta(days=8)
        },
        {
            "user_id": pm.id if pm else None,
            "action": "ALLOCATION_UPDATE",
            "entity_type": "allocation",
            "entity_id": 1,
            "details": {"project": "ECOM-2024", "hours_changed": "120 -> 160"},
            "timestamp": datetime.now() - timedelta(days=5)
        },
        {
            "user_id": admin.id if admin else None,
            "action": "ROLE_CREATE",
            "entity_type": "role",
            "entity_id": 10,
            "details": {"role_name": "Solutions Architect"},
            "timestamp": datetime.now() - timedelta(days=3)
        },
    ]

    for entry in audit_entries:
        existing = db.query(models.AuditLog).filter_by(
            action=entry["action"],
            entity_id=entry["entity_id"],
            timestamp=entry["timestamp"]
        ).first()

        if not existing:
            log = models.AuditLog(**entry)
            db.add(log)
            created += 1

    db.commit()
    print(f"✅ Created {created} audit log entries")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to seed all data"""
    print("=" * 80)
    print("StaffAlloc Comprehensive Database Seeding")
    print("=" * 80)
    print()

    db = SessionLocal()

    try:
        seed_roles(db)
        seed_lcats(db)
        seed_users(db)
        seed_projects(db)
        seed_assignments_and_allocations(db)
        seed_monthly_overrides(db)
        seed_ai_recommendations(db)
        seed_audit_logs(db)

        print()
        print("=" * 80)
        print("✅ Database seeding completed successfully!")
        print("=" * 80)
        print()
        print("📊 Database Summary:")
        print(f"   • {db.query(models.User).count()} Users")
        print(f"   • {db.query(models.Role).count()} Roles")
        print(f"   • {db.query(models.LCAT).count()} LCATs")
        print(f"   • {db.query(models.Project).count()} Projects")
        print(f"   • {db.query(models.ProjectAssignment).count()} Project Assignments")
        print(f"   • {db.query(models.Allocation).count()} Allocations")
        print(f"   • {db.query(models.MonthlyHourOverride).count()} Monthly Hour Overrides")
        print(f"   • {db.query(models.AIRecommendation).count()} AI Recommendations")
        print(f"   • {db.query(models.AuditLog).count()} Audit Log Entries")
        print()
        print("🔐 Test Credentials:")
        print("   Admin:")
        print("      Email: admin@staffalloc.com")
        print("      Password: admin123")
        print()
        print("   Project Managers:")
        print("      Email: david.kim@staffalloc.com")
        print("      Email: emily.johnson@staffalloc.com")
        print("      Password: password123")
        print()
        print("   All other users:")
        print("      Password: password123")
        print()

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

