# Migration Guide: Manager-Specific Data Isolation

## Overview

This guide documents the migration from a global data model to a manager-specific isolation model where each PM (Project Manager) owns and manages their own data workspace.

## Breaking Changes

### 1. Removed Director Role
- **What Changed**: The `Director` system role has been removed from the application
- **Migration**: All Director users will be converted to PM role
- **Impact**: 
  - Login screen no longer shows Director option
  - Navigation and permissions simplified to PM and Admin only

### 2. Mandatory Manager Context
- **What Changed**: All API endpoints now require `manager_id` parameter for data filtering
- **Migration**: Frontend automatically passes logged-in user's ID
- **Impact**: 
  - Projects API: `/api/v1/projects?manager_id=X` (required)
  - Employees API: `/api/v1/employees?manager_id=X` (required)
  - Roles API: `/api/v1/admin/roles/?owner_id=X` (required)
  - LCATs API: `/api/v1/admin/lcats/?owner_id=X` (required)
  - Portfolio Dashboard: `/api/v1/reports/portfolio-dashboard?manager_id=X` (required)

### 3. Removed ProjectViewer Functionality
- **What Changed**: Project sharing/viewer functionality removed
- **Rationale**: Contradicts manager-specific data isolation principle
- **Impact**: Managers can only view their own projects

### 4. Data Isolation Enforcement
- **What Changed**: All data is now scoped to manager ownership
- **Database**: 
  - `users.manager_id` required for Employee accounts
  - `roles.owner_id` required for all roles
  - `lcats.owner_id` required for all LCATs
  - `projects.manager_id` required for all projects

## Running the Migration

### Step 1: Backup Your Database
```bash
cp Artifacts/backend/data/staffalloc.db Artifacts/backend/data/staffalloc.db.backup
```

### Step 2: Run Migration Script
```bash
cd Artifacts/backend
python migrate_remove_director.py
```

This script will:
- Convert all Director users to PM role
- Assign orphaned projects to first available PM
- Assign orphaned employees to first available PM  
- Assign orphaned roles/LCATs to first available PM
- Add necessary indexes for performance

### Step 3: Verify Migration
```bash
python verify_seed.py
```

Check the output to ensure all data has proper ownership.

### Step 4: Seed Fresh Test Data (Optional)
For testing with multiple isolated managers:
```bash
python seed_multiple_managers.py
```

This creates:
- 3 Manager accounts with credentials
- 8-10 employees per manager
- 4-5 roles per manager
- 4-5 LCATs per manager
- 5-7 projects per manager with rich allocation data

## New Features

### Dashboard Allocation Rollup Grid
- **Endpoint**: `GET /api/v1/reports/manager-allocations`
- **Purpose**: Shows all employees for a manager with monthly allocation totals
- **Parameters**:
  - `manager_id` (required)
  - `start_year`, `start_month` (required)
  - `end_year`, `end_month` (required)
- **UI**: Replaces "FTE by Role" chart on Portfolio Dashboard

### Enhanced AI Features
1. **Auto-Running Conflict Monitor**: AI Assistant page automatically checks for conflicts on load
2. **AI Resolution Suggestions**: When conflicts detected, AI provides resolution suggestions
3. **Availability-Based Search**: AI chat supports queries like "Who is free to work 200 hours from Mar-Oct 2026?"
4. **Project-Scoped Chat**: Each project has its own AI chat for staffing questions

## API Changes Summary

### Required Parameters (New)
All endpoints now require manager/owner context:

| Endpoint | Old | New |
|----------|-----|-----|
| GET /projects | `manager_id` optional | `manager_id` **required** |
| GET /employees | `manager_id` optional | `manager_id` **required** |
| GET /admin/roles/ | `owner_id` optional, `include_global` option | `owner_id` **required**, no global |
| GET /admin/lcats/ | `owner_id` optional, `include_global` option | `owner_id` **required**, no global |
| GET /reports/portfolio-dashboard | No parameters | `manager_id` **required** |

### Removed Parameters
- `include_global` - no longer supported (all data is manager-specific)
- `viewer_user_id` - ProjectViewer functionality removed

### New Endpoints
- `GET /api/v1/reports/manager-allocations` - Dashboard rollup grid data

## Frontend Changes

### API Client Updates
All API functions now require manager context:

```typescript
// Old
fetchProjects({ managerId: user.id }) // optional

// New  
fetchProjects({ managerId: user.id }) // required

// Old
fetchRoles({ ownerId: user.id, includeGlobal: true })

// New
fetchRoles({ ownerId: user.id }) // no includeGlobal
```

### Component Updates
- **TeamsPage**: Now shows only manager's employees
- **ProjectsPage**: Now shows only manager's projects
- **PortfolioDashboard**: Shows manager-specific metrics + rollup grid
- **ProjectDetailPage**: AI chat moved below allocation grid
- **AIChatPage**: Auto-runs conflict detection, shows formatted conflicts

## Testing Data Isolation

### Manual Testing Steps
1. **Create 2+ manager accounts** via signup
2. **Login as Manager 1**, create:
   - 2-3 employees
   - 2 roles
   - 2 LCATs
   - 1 project with allocations
3. **Logout and login as Manager 2**, verify:
   - Dashboard shows 0 projects (not Manager 1's projects)
   - Teams page shows 0 employees (not Manager 1's employees)
   - Settings show 0 roles/LCATs (not Manager 1's data)
4. **Create data for Manager 2**, verify isolation maintained

### Automated Testing
Run existing test suite with manager context:
```bash
cd Artifacts/backend
pytest tests/ -v
```

## Rollback Procedure

If you need to rollback:

1. Restore database backup:
```bash
cp Artifacts/backend/data/staffalloc.db.backup Artifacts/backend/data/staffalloc.db
```

2. Revert code changes using git:
```bash
git checkout <previous-commit-hash>
```

## Troubleshooting

### Issue: API returns empty arrays
**Cause**: Missing manager_id parameter in API calls
**Fix**: Ensure all API calls pass user.id from AuthContext

### Issue: UNIQUE constraint failed during seeding
**Cause**: Database not fully wiped
**Fix**: Delete `staffalloc.db`, `staffalloc.db-shm`, `staffalloc.db-wal` files manually

### Issue: Frontend shows "User not authenticated"
**Cause**: User object missing in AuthContext
**Fix**: Check login flow, ensure user.id is set

## Login Credentials (Seed Data)

After running `seed_multiple_managers.py`:

**Managers:**
- sarah.martinez@staffalloc.com / manager123
- james.wilson@staffalloc.com / manager123
- aisha.patel@staffalloc.com / manager123

**Admin:**
- admin@staffalloc.com / admin123

## Support

For issues or questions about this migration, refer to:
- `Artifacts/Documentation/prd.md` - Product requirements
- `Artifacts/Documentation/architecture.md` - System architecture
- `INTEGRATION_GUIDE.md` - Integration documentation

