# Run StaffAlloc - Quick Command Reference

**Already set up?** Use these commands to start the application.

> **First time setup?** See [QUICKSTART.md](./QUICKSTART.md) for complete installation instructions.

---

## Start Backend (Terminal 1)

```bash
cd /path/to/220372-AG-AISOFTDEV-Team-1-AINavigators/Artifacts/backend
source ../../venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Backend will run on:** http://localhost:8000

---

## Start Frontend (Terminal 2)

```bash
cd /path/to/220372-AG-AISOFTDEV-Team-1-AINavigators/frontend
npm run dev
```

**Frontend will run on:** http://localhost:5173

---

## Login Credentials

**Admin:**
- Email: `admin@staffalloc.com`
- Password: `admin123`

**All other users:**
- Password: `password123`

---

## Quick Links

- **Application:** http://localhost:5173
- **API Docs:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/health

---

## Stop Servers

**Stop both servers:**
```bash
lsof -ti:8000 | xargs kill -9 && lsof -ti:5173 | xargs kill -9
```

**Or stop individually:**
```bash
# Stop backend
lsof -ti:8000 | xargs kill -9

# Stop frontend
lsof -ti:5173 | xargs kill -9
```

**Alternative:** Press `Ctrl+C` in each terminal window where the servers are running.

---

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

**Database issues?**
```bash
cd Artifacts/backend
rm -rf data/staffalloc.db*
python seed_data_comprehensive.py
```

---

**For detailed help:** See [QUICKSTART.md](./QUICKSTART.md)

