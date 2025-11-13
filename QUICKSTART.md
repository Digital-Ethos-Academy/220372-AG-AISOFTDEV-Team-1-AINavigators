# StaffAlloc - Quick Start Guide

Get the StaffAlloc application running in minutes! This guide covers setting up and running both the backend API and frontend React application.

---

## 📋 Prerequisites

### Required Software
- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+ and npm** - [Download Node.js](https://nodejs.org/)
- **SQLite 3** (usually pre-installed on macOS/Linux)

### Verify Installation
```bash
python --version   # Should show 3.10+
node --version     # Should show 18+
npm --version      # Should show 9+
sqlite3 --version  # Should show 3.x
```

---

## 🚀 Quick Start (Both Frontend & Backend)

### Step 1: Clone and Navigate to Project
```bash
cd /path/to/220372-AG-AISOFTDEV-Team-1-AINavigators
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment in project root
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Backend Dependencies
```bash
cd Artifacts/backend

# Install all required packages
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings \
    "python-jose[cryptography]" "passlib[bcrypt]" structlog httpx \
    ujson email-validator python-multipart
```

### Step 4: Set Up Database with Seed Data
```bash
# Still in Artifacts/backend directory
python seed_data_comprehensive.py
```

This creates a fully populated database with:
- 27 users (2 admins, 2 directors, 3 PMs, 20 employees)
- 20 roles (Software Engineer, QA Engineer, etc.)
- 8 LCATs (labor categories)
- 11 projects with realistic timelines
- 55+ project assignments
- 130+ monthly allocations
- AI recommendations and audit logs

### Step 5: Start the Backend Server
```bash
# In Artifacts/backend directory with venv activated
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Keep this terminal running!** The backend server needs to stay active.

### Step 6: Install Frontend Dependencies
Open a **new terminal** window/tab:

```bash
cd /path/to/220372-AG-AISOFTDEV-Team-1-AINavigators/frontend
npm install
```

### Step 7: Start the Frontend Server
```bash
# Still in frontend directory
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 8: Access the Application
Open your browser to: **http://localhost:5173**

---

## 🔐 Login Credentials

### Admin Account
- **Email:** `admin@staffalloc.com`
- **Password:** `admin123`

### Project Manager Accounts
- **Email:** `david.kim@staffalloc.com` or `emily.johnson@staffalloc.com`
- **Password:** `password123`

### All Other Users
- **Password:** `password123`

---

## ✅ Verify Everything Works

### 1. Check Backend Health
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

Note: `llm_service` is optional and requires Ollama setup.

### 2. View API Documentation
Backend provides interactive API docs:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

### 3. Test the Frontend
1. Navigate to http://localhost:5173
2. Log in with admin credentials
3. Navigate through:
   - **Dashboard** - See portfolio overview
   - **Projects** - View and create projects
   - **Allocations** - Manage project allocations
   - **Employees** - View team members

---

## 🛠 Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'email_validator'"
**Solution:**
```bash
pip install email-validator
```

#### "Form data requires 'python-multipart' to be installed"
**Solution:**
```bash
pip install python-multipart
```

#### "Port 8000 already in use"
**Solution:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
# Or use a different port
uvicorn app.main:app --reload --port 8001
```

#### "Database file not found" or "No such table"
**Solution:**
```bash
cd Artifacts/backend
python seed_data_comprehensive.py
```

### Frontend Issues

#### "Port 5173 already in use"
**Solution:**
```bash
# Find and kill process using port 5173
lsof -ti:5173 | xargs kill -9
# Restart frontend
npm run dev
```

#### "Network Error" or "Failed to fetch" in browser
**Solution:**
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Ensure `VITE_API_BASE_URL` is set correctly (defaults to http://localhost:8000/api/v1)

#### CORS Errors
**Solution:**
Backend is pre-configured for `http://localhost:5173`. If using a different port, update `Artifacts/backend/app/core/config.py`:
```python
BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:YOUR_PORT"]
```

---

## 📁 Project Structure

```
220372-AG-AISOFTDEV-Team-1-AINavigators/
├── Artifacts/
│   ├── backend/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py            # API entry point
│   │   │   ├── models.py          # SQLAlchemy models
│   │   │   ├── schemas.py         # Pydantic schemas
│   │   │   ├── crud.py            # Database operations
│   │   │   ├── api/               # API routers
│   │   │   │   ├── auth.py        # Authentication endpoints
│   │   │   │   ├── projects.py    # Project management
│   │   │   │   ├── employees.py   # Employee management
│   │   │   │   ├── allocations.py # Resource allocations
│   │   │   │   └── reports.py     # Dashboards & reports
│   │   │   ├── core/              # Core utilities
│   │   │   │   ├── config.py      # Configuration
│   │   │   │   └── security.py    # Auth & JWT
│   │   │   └── db/                # Database layer
│   │   │       └── session.py     # SQLAlchemy session
│   │   ├── data/
│   │   │   └── staffalloc.db      # SQLite database
│   │   ├── seed_data_comprehensive.py  # Database seeding script
│   │   └── QUICKSTART.md          # Backend-specific guide
│   │
│   ├── Documentation/
│   │   ├── prd.md                 # Product Requirements
│   │   └── architecture.md        # System Architecture
│   │
│   └── schema.sql                 # Database schema
│
├── frontend/                       # React + TypeScript frontend
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                 # Page components
│   │   │   ├── LoginPage.tsx      # Login page
│   │   │   ├── DashboardPage.tsx  # Main dashboard
│   │   │   ├── ProjectsPage.tsx   # Projects view
│   │   │   ├── AllocationsPage.tsx # Allocations view
│   │   │   └── EmployeesPage.tsx  # Employees view
│   │   ├── services/              # API client services
│   │   │   ├── auth.ts            # Authentication
│   │   │   ├── projects.ts        # Project API calls
│   │   │   └── allocations.ts     # Allocation API calls
│   │   ├── contexts/              # React contexts
│   │   │   └── AuthContext.tsx    # Auth state management
│   │   └── types/                 # TypeScript types
│   ├── package.json
│   └── vite.config.ts
│
├── venv/                          # Python virtual environment
├── README.md                      # Project overview
└── QUICKSTART.md                  # This file!
```

---

## 🛑 Stopping the Application

To shut down both servers:

```bash
# Stop both at once
lsof -ti:8000 | xargs kill -9 && lsof -ti:5173 | xargs kill -9

# Or stop individually
lsof -ti:8000 | xargs kill -9  # Stop backend
lsof -ti:5173 | xargs kill -9  # Stop frontend
```

**Alternative:** If you can see the terminal windows, press `Ctrl+C` in each one.

---

## 🔄 Common Workflows

### Resetting the Database
If you need to start fresh:
```bash
cd Artifacts/backend
rm -rf data/staffalloc.db data/staffalloc.db-shm data/staffalloc.db-wal
python seed_data_comprehensive.py
```

### Running Backend Without Auto-Reload
For production-like testing:
```bash
uvicorn app.main:app --port 8000
```

### Building Frontend for Production
```bash
cd frontend
npm run build
# Output will be in frontend/dist/
```

### Running Tests
Backend tests (if available):
```bash
cd Artifacts/backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

---

## 🌐 API Endpoints Overview

### Authentication (`/api/v1/auth`)
- `POST /login` - Login with email/password
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user info

### Projects (`/api/v1/projects`)
- `GET /` - List all projects
- `POST /` - Create new project
- `GET /{id}` - Get project details
- `PUT /{id}` - Update project
- `DELETE /{id}` - Delete project
- `GET /{id}/assignments` - Get project assignments

### Employees (`/api/v1/employees`)
- `GET /` - List all employees
- `POST /` - Create employee
- `GET /{id}` - Get employee details
- `PUT /{id}` - Update employee
- `DELETE /{id}` - Delete employee

### Allocations (`/api/v1/allocations`)
- `GET /` - List all allocations with details
- `POST /` - Create allocation
- `PUT /{id}` - Update allocation
- `DELETE /{id}` - Delete allocation
- `POST /assignments` - Assign employee to project
- `GET /users/{id}/summary` - Get user allocation summary

### Reports (`/api/v1/reports`)
- `GET /portfolio-dashboard` - Organization-wide metrics
- `GET /project-dashboard/{id}` - Project-specific dashboard
- `GET /employee-timeline/{id}` - Employee allocation timeline

### Admin (`/api/v1/admin`)
- `GET /roles/` - List all roles
- `POST /roles/` - Create new role
- `GET /lcats/` - List all LCATs
- `POST /lcats/` - Create new LCAT
- `GET /audit-logs/` - View audit trail
- `GET /recommendations/` - View AI recommendations

---

## 📚 Additional Resources

- **Product Requirements:** `Artifacts/Documentation/prd.md`
- **Architecture Document:** `Artifacts/Documentation/architecture.md`
- **Database Schema:** `Artifacts/schema.sql`
- **Backend Details:** `Artifacts/backend/QUICKSTART.md`
- **Testing Checklist:** `TESTING_CHECKLIST.md`

---

## 🆘 Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Verify all prerequisites are installed
3. Ensure you're in the correct directory
4. Check that both servers are running
5. Review browser console and terminal logs for error messages

---

## 🎉 You're All Set!

Your StaffAlloc application should now be running with:
- ✅ Backend API on http://localhost:8000
- ✅ Frontend UI on http://localhost:5173
- ✅ Interactive API docs on http://localhost:8000/api/docs
- ✅ Database populated with realistic demo data

**Enjoy exploring the application!** 🚀

