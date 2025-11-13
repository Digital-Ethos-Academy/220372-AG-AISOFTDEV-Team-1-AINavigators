# StaffAlloc Backend - Quick Start Guide

This guide provides backend-specific details for the StaffAlloc API server.

> **📘 New to this project?** For complete setup instructions including both frontend and backend, see the main **[QUICKSTART.md](../../QUICKSTART.md)** in the project root.

---

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- SQLite 3 (usually pre-installed on most systems)

---

## Installation Steps

### 1. Navigate to Backend Directory

```bash
cd Artifacts/backend
```

### 2. Install Python Dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings \
    "python-jose[cryptography]" "passlib[bcrypt]" structlog httpx ujson \
    email-validator python-multipart
```

Or if you prefer using a virtual environment (recommended):

```bash
# Create virtual environment (from project root)
python -m venv ../../venv

# Activate it
# On Windows:
..\..\venv\Scripts\activate
# On macOS/Linux:
source ../../venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings \
    "python-jose[cryptography]" "passlib[bcrypt]" structlog httpx ujson \
    email-validator python-multipart
```

**Note:** `email-validator` is required by Pydantic for email field validation, and `python-multipart` is required for FastAPI to parse OAuth2 form data.

### 3. Create Data Directory

```bash
mkdir -p data
```

### 4. Initialize Database with Seed Data

The easiest way to set up the database is to run the comprehensive seed script, which creates all tables and populates them with demo data:

```bash
python seed_data_comprehensive.py
```

This will create:
- 27 users (2 admins, 2 directors, 3 PMs, 20 employees)
- 20 roles (Software Engineer, QA Engineer, Project Manager, etc.)
- 8 LCATs (Level 1-5, Senior, Principal, Distinguished)
- 11 projects with realistic timelines
- 55+ project assignments
- 130+ monthly allocations
- 6 monthly hour overrides
- 5 AI recommendations
- 5 audit log entries

**Default Admin Credentials:**
- Email: `admin@staffalloc.com`
- Password: `admin123`

**Alternative:** If you want an empty database without seed data:

```bash
python -c "from app.db.session import create_db_and_tables; create_db_and_tables()"
```

---

## Running the Application

### Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Verify Installation

### 1. Check Health Endpoint

Open your browser or use curl:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "dependencies": {
    "database": "ok",
    "llm_service": "unavailable"
  }
}
```

Note: `llm_service` will show as "unavailable" until you set up Ollama (optional for MVP).

### 2. Access API Documentation

Open your browser:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

You should see all available endpoints with interactive documentation.

### 3. Test a Simple Endpoint

Get all roles:
```bash
curl http://localhost:8000/api/v1/admin/roles/
```

Expected response (if seed data loaded):
```json
[
  {
    "name": "Project Manager",
    "description": "Manages project timelines, resources, and budget.",
    "id": 1,
    "created_at": "...",
    "updated_at": "..."
  },
  ...
]
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"

**Solution:** Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

Or install packages individually as shown in step 2.

### Issue: "No module named 'app'"

**Solution:** Make sure you're in the `Artifacts/backend` directory and run:
```bash
cd Artifacts/backend
uvicorn app.main:app --reload
```

### Issue: "Database file not found"

**Solution:** Create the data directory and initialize the database:
```bash
mkdir -p data
python -c "from app.db.session import create_db_and_tables; create_db_and_tables()"
```

### Issue: "Port 8000 already in use"

**Solution:** Either:
1. Stop the process using port 8000
2. Use a different port: `uvicorn app.main:app --reload --port 8001`

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   │
│   ├── api/                 # API routers
│   │   ├── admin.py         # Roles, LCATs, audit logs
│   │   ├── ai.py            # AI features (placeholder)
│   │   ├── allocations.py   # Assignments & allocations
│   │   ├── employees.py     # Employee management
│   │   ├── projects.py      # Project management
│   │   └── reports.py       # Dashboards & reports
│   │
│   ├── core/                # Core utilities
│   │   ├── config.py        # Configuration
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── security.py      # Auth & password hashing
│   │
│   └── db/                  # Database layer
│       └── session.py       # Session management
│
└── data/                    # Local data (not in git)
    └── staffalloc.db        # SQLite database
```

---

## Next Steps

### For Development

1. **Add Authentication**
   - Implement login endpoint
   - Add `Depends(get_current_user)` to protected routes

2. **Write Tests**
   - Set up pytest
   - Write unit tests for CRUD operations
   - Write integration tests for API endpoints

3. **Enhance Validation**
   - Add business rule validation
   - Improve error messages

### For Production (Future)

1. **Set up Alembic** for database migrations
2. **Configure CORS** for your frontend domain
3. **Set up proper logging** and monitoring
4. **Use environment variables** for secrets
5. **Deploy to cloud** (see architecture.md for migration path)

---

## API Endpoints Overview

### Projects (`/api/v1/projects`)
- `POST /` - Create project
- `GET /` - List projects
- `GET /{id}` - Get project details
- `PUT /{id}` - Update project
- `DELETE /{id}` - Delete project
- `POST /overrides` - Create monthly hour override

### Employees (`/api/v1/employees`)
- `POST /` - Create employee
- `GET /` - List employees
- `GET /{id}` - Get employee with assignments
- `PUT /{id}` - Update employee
- `DELETE /{id}` - Delete employee

### Allocations (`/api/v1/allocations`)
- `POST /assignments` - Assign employee to project
- `POST /` - Create allocation (monthly hours)
- `GET /{id}` - Get allocation
- `PUT /{id}` - Update allocation
- `DELETE /{id}` - Delete allocation
- `GET /users/{id}/summary` - Get user's FTE summary

### Admin (`/api/v1/admin`)
- `POST /roles/` - Create role
- `GET /roles/` - List roles
- `POST /lcats/` - Create LCAT
- `GET /lcats/` - List LCATs
- `GET /audit-logs/` - View audit logs
- `GET /recommendations/` - View AI recommendations

### Reports (`/api/v1/reports`)
- `GET /portfolio-dashboard` - Organization-wide dashboard
- `GET /project-dashboard/{id}` - Project-specific dashboard
- `GET /employee-timeline/{id}` - Employee allocation timeline
- `GET /export/portfolio` - Export to Excel (placeholder)

### AI (`/api/v1/ai`)
- `POST /chat` - RAG chat query (placeholder)
- `POST /recommend-staff` - Get staffing recommendations (placeholder)
- `GET /conflicts` - Detect over-allocations (placeholder)
- `GET /forecast` - Resource forecasting (placeholder)

---

## Support & Resources

- **Architecture Document:** `Artifacts/Documentation/architecture.md`
- **PRD:** `Artifacts/Documentation/prd.md`
- **Database Schema:** `Artifacts/schema.sql`
- **Review Report:** `Artifacts/backend/BACKEND_REVIEW.md`
- **Fixes Applied:** `Artifacts/backend/FIXES_APPLIED.md`

---

## Need Help?

If you encounter issues:

1. Check the **Common Issues** section above
2. Review the **BACKEND_REVIEW.md** for detailed information
3. Verify all dependencies are installed correctly
4. Make sure you're running commands from the correct directory

---

**Happy Coding!** 🚀

