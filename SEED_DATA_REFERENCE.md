# StaffAlloc - Seed Data Reference Guide

This document provides a comprehensive overview of the seed data loaded into the StaffAlloc application, helping you understand and test all features of the system.

---

## 🚀 Quick Start

**Backend API**: http://localhost:8000  
**Frontend UI**: http://localhost:5173  
**API Documentation**: http://localhost:8000/api/docs

---

## 🔐 Test Accounts

### Administrator Account
```
Email: admin@staffalloc.com
Password: admin123
System Role: Admin
```
**Capabilities**: Full system access, manage roles/LCATs, view all projects and allocations

### Project Manager Accounts
```
Email: david.kim@staffalloc.com
Password: password123
System Role: PM
```
```
Email: emily.johnson@staffalloc.com
Password: password123
System Role: PM
```
```
Email: james.williams@staffalloc.com
Password: password123
System Role: PM
```
**Capabilities**: Manage projects, create assignments, view team allocations

### Director Accounts
```
Email: michael.rodriguez@staffalloc.com
Password: password123
System Role: Director
```
```
Email: jennifer.patel@staffalloc.com
Password: password123
System Role: Director
```
**Capabilities**: High-level oversight, portfolio dashboards, strategic planning

### Employee Accounts (Sample)
All employees use the password: `password123`

- alex.thompson@staffalloc.com
- maria.garcia@staffalloc.com
- robert.brown@staffalloc.com
- lisa.anderson@staffalloc.com
- kevin.martinez@staffalloc.com
- amanda.taylor@staffalloc.com
- ... and 18 more active employees!

---

## 📊 Database Contents Summary

| Entity | Count | Description |
|--------|-------|-------------|
| **Users** | 27 | Employees, PMs, Directors, and Admins |
| **Roles** | 20 | Job roles from Software Engineer to Solutions Architect |
| **LCATs** | 8 | Labor categories from Junior (L1) to Director |
| **Projects** | 11 | Mix of Active, Planning, On Hold, and Closed projects |
| **Project Assignments** | 56 | Employee-to-project assignments with roles and funded hours |
| **Allocations** | 129 | Monthly hour allocations across all assignments |
| **Monthly Hour Overrides** | 6 | Custom hour overrides for specific months |
| **AI Recommendations** | 5 | Intelligent staffing and workload suggestions |
| **Audit Log Entries** | 5 | System activity tracking |

---

## 🏗️ Projects Overview

### Active Projects (6)

1. **ECOM-2024** - E-Commerce Platform Modernization
   - Client: RetailMax Inc.
   - Started: ~4 months ago
   - Duration: 24 sprints
   - Team: 5-8 employees
   - Status: Actively in progress

2. **MOBILE-IOS** - iOS Mobile App Development
   - Client: TechCorp Solutions
   - Started: ~3 months ago
   - Duration: 16 sprints
   - Status: Active development

3. **DATA-DASH** - Executive Analytics Dashboard
   - Client: FinanceHub Global
   - Started: ~2 months ago
   - Duration: 12 sprints
   - Status: Active development

4. **AI-CHAT** - AI-Powered Customer Support
   - Client: ServiceDesk Pro
   - Started: ~1.5 months ago
   - Duration: 18 sprints
   - Status: Active development

5. **LEGACY-MIG** - Legacy System Migration
   - Client: BankCorp International
   - Started: ~5 months ago
   - Duration: 32 sprints (long-term)
   - Status: Active - complex migration project

6. **HEALTH-APP** - Healthcare Patient Portal
   - Client: MediCare Systems
   - Started: ~1 month ago
   - Duration: 20 sprints
   - Status: Active development

### Planning Projects (3)

7. **CLOUD-INFRA** - Cloud Infrastructure Upgrade
   - Client: DataCenter Corp
   - Starts: In 2 weeks
   - Duration: 10 sprints
   - Status: Planning phase

8. **RETAIL-POS** - Point of Sale System
   - Client: ShopMart Retail
   - Starts: In 1 month
   - Duration: 14 sprints
   - Status: Planning phase

9. **IOT-PLATFORM** - IoT Device Management Platform
   - Client: SmartHome Industries
   - Starts: In 1.5 months
   - Duration: 16 sprints
   - Status: Planning phase

### On Hold Projects (1)

10. **BLOCKCHAIN** - Blockchain Supply Chain
    - Client: LogisticsCo
    - Started: ~2.5 months ago
    - Duration: 20 sprints
    - Status: On Hold (awaiting client decision)

### Closed Projects (1)

11. **WEB-REDESIGN** - Corporate Website Redesign
    - Client: BrandCompany LLC
    - Started: ~6.5 months ago
    - Duration: 8 sprints
    - Status: Successfully completed

---

## 👥 Roles & Labor Categories

### Roles (20 Total)

**Engineering Roles:**
- Software Engineer
- Senior Software Engineer
- Staff Software Engineer
- Frontend Developer
- Backend Developer
- Full Stack Developer
- Mobile Developer

**Specialized Roles:**
- Data Scientist
- Senior Data Scientist
- DevOps Engineer
- Site Reliability Engineer
- Security Engineer
- QA Engineer
- QA Lead

**Leadership Roles:**
- Engineering Manager
- Tech Lead
- Solutions Architect
- Product Manager
- Product Designer
- Senior Product Designer

### Labor Categories (LCATs)

| LCAT | Description | Experience |
|------|-------------|------------|
| Junior (L1) | Entry-level | 0-2 years |
| Intermediate (L2) | Mid-level | 2-5 years |
| Senior (L3) | Senior professional | 5-8 years |
| Staff (L4) | Expert level | 8-12 years |
| Principal (L5) | Principal expert | 12+ years |
| Manager | People management | Varies |
| Senior Manager | Senior management | Varies |
| Director | Leadership | Varies |

---

## 📅 Allocation Patterns

The seed data includes realistic allocation patterns:

### Pattern Types

1. **Full-Time Allocation**: 160 hours/month (100% capacity)
2. **Part-Time Allocation**: 80 hours/month (50% capacity)
3. **Ramping Up**: 40 → 80 → 120 → 160 hours (gradual onboarding)
4. **Ramping Down**: 160 → 120 → 80 → 40 hours (project conclusion)
5. **Variable Allocation**: 120 → 80 → 160 → 100 hours (dynamic needs)

### Allocation Timeline

- **Active Projects**: Have allocations for the past 1-6 months
- **Planning Projects**: No allocations yet (will start in the future)
- **On Hold Projects**: Partial allocations (2-4 months)
- **Closed Projects**: Complete historical allocations (6 months)

### Over-Allocation Scenario

At least one employee (Alex Thompson) is intentionally over-allocated in a specific month to demonstrate the conflict detection feature:
- Total allocation: 220 hours in December 2024
- Across 2 projects
- AI recommendation suggests resolution

---

## 🤖 AI Recommendations (5 Examples)

### 1. Staffing Recommendation
```
Type: STAFFING
Project: ECOM-2024
Suggestion: Add 1 Senior Software Engineer for Q1 2025
Reason: Based on project velocity to meet sprint goals
Status: Pending
```

### 2. Conflict Resolution
```
Type: CONFLICT_RESOLUTION
Employee: Alex Thompson
Issue: Over-allocated in December 2024 (220 hours)
Suggestion: Reduce DATA-DASH allocation by 60 hours
Status: Pending
```

### 3. Workload Balance
```
Type: WORKLOAD_BALANCE
Project: MOBILE-IOS
Issue: 3 engineers at 100% capacity
Suggestion: Add 1 mid-level engineer or adjust scope
Status: Accepted
```

### 4. Resource Forecast
```
Type: FORECAST
Project: LEGACY-MIG
Prediction: Needs 200 additional hours in Q1 2025
Reason: Based on current burn rate
Status: Pending
```

### 5. Staffing for Upcoming Project
```
Type: STAFFING
Project: CLOUD-INFRA
Need: 2 DevOps Engineers
Available: Brandon Harris, Jason Lewis
Status: Dismissed
```

---

## ⏰ Monthly Hour Overrides

Custom work-hour definitions for specific months:

### Current Month Overrides (Holiday Period)
- **3 Projects**: Reduced from standard 160 to 140 hours
- **Reason**: Holiday period with reduced availability

### Next Month Overrides (Extended Hours)
- **3 Projects**: Extended from 160 to 176 hours
- **Reason**: Sprint deadline push or extended work period

---

## 📝 Audit Log Sample

Recent system activities tracked:

1. **User Creation**: New employee account created
2. **Project Creation**: ECOM-2024 project initiated
3. **Assignment Creation**: Alex Thompson assigned to ECOM-2024
4. **Allocation Update**: Hours adjusted from 120 to 160
5. **Role Creation**: New "Solutions Architect" role added

---

## 🧪 Testing Scenarios

### Scenario 1: Dashboard Overview
**Goal**: View organization-wide staffing status

1. Login as Director (michael.rodriguez@staffalloc.com)
2. Navigate to Dashboard
3. Observe:
   - 11 total projects
   - 27 active employees
   - Current month allocations across teams
   - AI recommendations summary

### Scenario 2: Project Management
**Goal**: Manage a specific project's team

1. Login as PM (david.kim@staffalloc.com)
2. Navigate to Projects
3. Select "ECOM-2024"
4. View:
   - Team members (5-8 people)
   - Individual allocations by month
   - Funded vs. actual hours
   - Project timeline

### Scenario 3: Employee Allocation
**Goal**: View an employee's workload

1. Navigate to Employees
2. Select "Alex Thompson"
3. Observe:
   - Current projects assigned
   - Monthly allocation breakdown
   - Total FTE percentage
   - **Over-allocation warning** in December 2024

### Scenario 4: Allocation Grid
**Goal**: Edit monthly allocations

1. Navigate to Projects → MOBILE-IOS
2. Click "Allocation Grid"
3. View:
   - Monthly allocation matrix
   - Each team member's hours by month
   - Total project hours per month
   - Edit capabilities (if PM/Admin)

### Scenario 5: AI Recommendations
**Goal**: Review and act on AI suggestions

1. Login as Admin or Director
2. Navigate to AI Recommendations (or Dashboard)
3. Review 5 pending/accepted recommendations
4. Accept, reject, or dismiss recommendations
5. Observe: Conflict detection for Alex Thompson

### Scenario 6: Monthly Overrides
**Goal**: Customize work hours for a specific month

1. Login as PM
2. Navigate to specific project
3. Set monthly override for holiday period (e.g., 140 hours)
4. View updated allocation calculations

### Scenario 7: Audit Trail
**Goal**: Review system activity

1. Login as Admin
2. Navigate to Admin → Audit Logs
3. Review:
   - Recent user actions
   - Project/allocation changes
   - Who made what changes and when

---

## 🔍 API Testing Examples

### Get All Projects
```bash
curl http://localhost:8000/api/v1/projects/ | python3 -m json.tool
```

### Get Specific Project with Assignments
```bash
curl http://localhost:8000/api/v1/projects/1 | python3 -m json.tool
```

### Get All Employees
```bash
curl http://localhost:8000/api/v1/employees/ | python3 -m json.tool
```

### Get Employee with Allocations
```bash
curl http://localhost:8000/api/v1/employees/7 | python3 -m json.tool
```

### Get AI Recommendations
```bash
curl http://localhost:8000/api/v1/admin/recommendations/ | python3 -m json.tool
```

### Get Roles
```bash
curl http://localhost:8000/api/v1/admin/roles/ | python3 -m json.tool
```

### Get LCATs
```bash
curl http://localhost:8000/api/v1/admin/lcats/ | python3 -m json.tool
```

### Get Portfolio Dashboard
```bash
curl http://localhost:8000/api/v1/reports/portfolio-dashboard | python3 -m json.tool
```

### Get Employee FTE Summary
```bash
curl http://localhost:8000/api/v1/allocations/users/7/summary?year=2024&month=11 | python3 -m json.tool
```

---

## 📈 Key Metrics

### Resource Utilization
- **Total Available Capacity**: 27 employees × 160 hours = 4,320 hours/month
- **Active Allocations**: ~129 allocation records across active projects
- **Average Team Size**: 5-8 people per active project

### Project Portfolio
- **Active**: 55% (6 projects)
- **Planning**: 27% (3 projects)
- **On Hold**: 9% (1 project)
- **Closed**: 9% (1 project)

### Role Distribution
- Engineering roles: 14 types
- Specialized roles: 4 types
- Leadership roles: 2 types

---

## 🎯 Feature Coverage

The seed data demonstrates:

✅ **User Management** - Multiple roles and permissions  
✅ **Project Lifecycle** - All statuses (Planning → Active → On Hold/Closed)  
✅ **Team Assignments** - Employees assigned to multiple projects  
✅ **Monthly Allocations** - Realistic hour distributions  
✅ **FTE Tracking** - Cross-project workload monitoring  
✅ **Over-Allocation Detection** - Conflict scenarios  
✅ **Monthly Overrides** - Custom work-hour definitions  
✅ **AI Recommendations** - Intelligent suggestions  
✅ **Audit Logging** - Activity tracking  
✅ **Role/LCAT Management** - Standardized taxonomies  

---

## 🔄 Regenerating Seed Data

To regenerate the seed data from scratch:

```bash
# Navigate to backend directory
cd Artifacts/backend

# Activate virtual environment
source ../../venv/bin/activate

# Delete existing database (WARNING: This deletes ALL data!)
rm data/staffalloc.db

# Recreate database schema
python -c "from app.db.session import create_db_and_tables; create_db_and_tables()"

# Run comprehensive seed script
python seed_data_comprehensive.py
```

---

## 💡 Tips for Demonstration

1. **Start with Dashboard**: Shows high-level overview of the entire system
2. **Show Project Details**: Pick ECOM-2024 or MOBILE-IOS for rich data
3. **Demonstrate Conflict**: Use Alex Thompson to show over-allocation warning
4. **Highlight AI**: Show the 5 AI recommendations with different statuses
5. **Show Timeline**: Use employee view to show workload over time
6. **Interactive Editing**: Modify allocations in the allocation grid
7. **Audit Trail**: Show how changes are tracked

---

## 📞 Support

If you need to:
- Reset the database: Delete `data/staffalloc.db` and rerun seed script
- Add more data: Modify `seed_data_comprehensive.py` and rerun
- Test specific scenarios: Use the API testing examples above

---

**Generated**: November 6, 2025  
**Version**: 1.0  
**Application**: StaffAlloc - AI-Powered Staffing Management Platform

