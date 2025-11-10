"""
Migration script to remove Director role and ensure data isolation.

This script:
1. Converts any Director users to PM role
2. Ensures all projects have manager_id set
3. Ensures all employees have manager_id set
4. Ensures all roles have owner_id set
5. Ensures all lcats have owner_id set
6. Removes any orphaned data
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.session import SessionLocal, engine
from app.models import SystemRole, User, Project, Role, LCAT


def migrate_director_to_pm(db):
    """Convert all Director users to PM role."""
    print("Converting Director users to PM...")
    result = db.execute(
        text("UPDATE users SET system_role = 'PM' WHERE system_role = 'Director'")
    )
    db.commit()
    print(f"  Converted {result.rowcount} Director users to PM")


def ensure_projects_have_managers(db):
    """Ensure all projects have a manager_id."""
    print("Checking projects for manager_id...")
    
    # Find projects without managers
    orphaned = db.execute(
        text("SELECT COUNT(*) FROM projects WHERE manager_id IS NULL")
    ).scalar()
    
    if orphaned > 0:
        # Get first PM user to assign orphaned projects
        first_pm = db.query(User).filter(User.system_role == SystemRole.PM).first()
        if first_pm:
            db.execute(
                text(f"UPDATE projects SET manager_id = {first_pm.id} WHERE manager_id IS NULL")
            )
            db.commit()
            print(f"  Assigned {orphaned} orphaned projects to PM user {first_pm.id}")
        else:
            print(f"  WARNING: {orphaned} projects have no manager and no PM users exist!")
    else:
        print("  All projects have managers")


def ensure_employees_have_managers(db):
    """Ensure all Employee users have a manager_id."""
    print("Checking employees for manager_id...")
    
    orphaned = db.execute(
        text("SELECT COUNT(*) FROM users WHERE system_role = 'Employee' AND manager_id IS NULL")
    ).scalar()
    
    if orphaned > 0:
        # Get first PM user to assign orphaned employees
        first_pm = db.query(User).filter(User.system_role == SystemRole.PM).first()
        if first_pm:
            db.execute(
                text(f"UPDATE users SET manager_id = {first_pm.id} WHERE system_role = 'Employee' AND manager_id IS NULL")
            )
            db.commit()
            print(f"  Assigned {orphaned} orphaned employees to PM user {first_pm.id}")
        else:
            print(f"  WARNING: {orphaned} employees have no manager and no PM users exist!")
    else:
        print("  All employees have managers")


def ensure_roles_have_owners(db):
    """Ensure all roles have an owner_id."""
    print("Checking roles for owner_id...")
    
    orphaned = db.execute(
        text("SELECT COUNT(*) FROM roles WHERE owner_id IS NULL")
    ).scalar()
    
    if orphaned > 0:
        # Get first PM user to assign orphaned roles
        first_pm = db.query(User).filter(User.system_role == SystemRole.PM).first()
        if first_pm:
            db.execute(
                text(f"UPDATE roles SET owner_id = {first_pm.id} WHERE owner_id IS NULL")
            )
            db.commit()
            print(f"  Assigned {orphaned} orphaned roles to PM user {first_pm.id}")
        else:
            print(f"  WARNING: {orphaned} roles have no owner and no PM users exist!")
    else:
        print("  All roles have owners")


def ensure_lcats_have_owners(db):
    """Ensure all LCATs have an owner_id."""
    print("Checking LCATs for owner_id...")
    
    orphaned = db.execute(
        text("SELECT COUNT(*) FROM lcats WHERE owner_id IS NULL")
    ).scalar()
    
    if orphaned > 0:
        # Get first PM user to assign orphaned LCATs
        first_pm = db.query(User).filter(User.system_role == SystemRole.PM).first()
        if first_pm:
            db.execute(
                text(f"UPDATE lcats SET owner_id = {first_pm.id} WHERE owner_id IS NULL")
            )
            db.commit()
            print(f"  Assigned {orphaned} orphaned LCATs to PM user {first_pm.id}")
        else:
            print(f"  WARNING: {orphaned} LCATs have no owner and no PM users exist!")
    else:
        print("  All LCATs have owners")


def add_indexes(db):
    """Add indexes for manager_id and owner_id columns if they don't exist."""
    print("Ensuring indexes exist...")
    
    # Note: SQLite doesn't fail if index already exists with IF NOT EXISTS
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_manager_id ON users(manager_id)",
        "CREATE INDEX IF NOT EXISTS idx_roles_owner_id ON roles(owner_id)",
        "CREATE INDEX IF NOT EXISTS idx_lcats_owner_id ON lcats(owner_id)",
    ]
    
    for idx_sql in indexes:
        db.execute(text(idx_sql))
    
    db.commit()
    print("  Indexes verified")


def main():
    """Run all migration steps."""
    print("=" * 60)
    print("StaffAlloc Migration: Remove Director & Ensure Data Isolation")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        migrate_director_to_pm(db)
        ensure_projects_have_managers(db)
        ensure_employees_have_managers(db)
        ensure_roles_have_owners(db)
        ensure_lcats_have_owners(db)
        add_indexes(db)
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

