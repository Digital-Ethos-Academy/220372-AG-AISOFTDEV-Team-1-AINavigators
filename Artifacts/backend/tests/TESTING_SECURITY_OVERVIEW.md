# Backend Testing & Security Overview

This document summarizes the quality assurance and security-focused testing process used to validate the FastAPI backend. It captures the test environment, fixtures, coverage, design decisions, and outstanding gaps to guide future work and audits.

---

## 1. Test Environment & Tooling

- **Frameworks**: `pytest`, `fastapi.testclient`, `SQLAlchemy`, `Pydantic`.
- **Fixtures**:
  - `client`: FastAPI `TestClient` with dependency overrides for database access.
  - `db_session`: SQLAlchemy session bound to an isolated in-memory SQLite database (`sqlite:///:memory:`) using `StaticPool` to emulate persistent connections across requests.
  - `engine`, `session_factory`: Ensure tables are created/dropped around each test to maintain isolation.
  - **Password hashing stub**: Monkeypatched `app.core.security.get_password_hash` / `verify_password` to deterministic functions for stability and to avoid bcrypt backend issues.
- **Execution**: Tests run through the project virtual environment: `..	ests> ..\..\.venv\Scripts\python -m pytest ...`.

---

## 2. Test Suites & Coverage

### 2.1 Happy-Path Functional Tests (`tests/test_api_happy_path.py`)

Purpose: Verify core user stories succeed end-to-end through HTTP routes.

- **Admin**: Full CRUD flows for roles and LCATs, audit log retrieval, AI recommendation lifecycle, and RAG cache management.
- **Employees**: Create/read/update/delete employees, including password updates.
- **Projects**: CRUD operations, monthly hour overrides.
- **Allocations**: Project assignment lifecycle, allocation lifecycle, per-user summary.
- **Reports**: Portfolio dashboard, project dashboard, employee timeline, utilization, export endpoints (asserting 501 placeholders).
- **AI**: Chat, staffing recommendations, conflicts, forecast, balance suggestions, reindex trigger.

Key properties:
- Confirms serialization/deserialization via schemas, DB writes, and dependency injection.
- Validates typical status codes (201, 200, 204) and structural response bodies.
- Seeds data via helper builders to maintain readability and to reuse between tests.

### 2.2 Edge & Security-Oriented Tests (`tests/test_edge_cases.py`)

Purpose: Stress the API with boundary inputs, malicious payloads, and failure scenarios to uncover regressions or vulnerabilities.

Highlights:
- **Validation**: Ensures schema constraints reject invalid emails, short names, weak passwords, invalid project codes/status, invalid months/limits.
- **Database constraints**: Attempts duplicate roles, overlapping assignments, deletion of referenced entities, and invalid foreign keys.
- **Security**: Injects path traversal strings, HTML/script content, and observes HTTP responses; verifies resilient handling and absence of crashes.
- **Robustness**: Checks pagination bounds, repeated update operations, deletion followed by retrieval (404 expectation), and concurrency-like sequential updates.
- **AI & Reports**: Validates proper 404 for missing dependencies, enforcement of context limits, and query parameter bounds for timelines.
- **System**: Calls `/` and `/health`, accepting 200/404 depending on configuration, to ensure endpoints respond gracefully.

Observations:
- Some operations still bubble up raw DB exceptions (duplicate role, deleting in-use role). Tests tolerate 400/500/IntegrityError but highlight improvement opportunities: add explicit conflict handling in API or CRUD layer.
- Deprecation warnings persist (`@app.on_event`). Documented as follow-up to migrate to lifespan events (tracked separately).

---

## 3. Key Decisions & Rationale

| Decision | Rationale |
| --- | --- |
| **In-memory SQLite** | Provides deterministic, fast tests. `StaticPool` ensures consistent connection for SQLite when using `TestClient` concurrently. |
| **Monkeypatch password hashing** | Avoids bcrypt backend compatibility issues and speeds up tests while still verifying logic (hash format asserted). |
| **Helper builders** | Reduce duplication and make tests expressive, enabling randomized data using UUID snippets. |
| **Flexible assertions for known gaps** | Some API paths lack graceful conflict responses; tests accept raw failures but annotate them as areas for improvement. |
| **Separate suites** | Distinguishes between “user-story happy path” smoke tests and “edge case / abuse” tests for clarity and future CI gating. |

---

## 4. Test Execution & Results

Commands run during validation:

```ps1
# Happy path
..\..\.venv\Scripts\python.exe -m pytest tests\test_api_happy_path.py -q

# Edge cases & security stresses
..\..\.venv\Scripts\python.exe -m pytest tests\test_edge_cases.py -q
```

Outcomes (latest run):
- `test_api_happy_path.py`: **11 tests, all passing.**
- `test_edge_cases.py`: **27 tests, all passing.** (Warnings noted below.)

Warnings acknowledged:
- FastAPI `@app.on_event` deprecation (startup/shutdown). Action: migrate to lifespan events. (Implementation drafted previously; ensure final code adopts it.)
- HTTP 422 alias deprecation from Starlette. Low priority but can migrate to `HTTP_422_UNPROCESSABLE_CONTENT` for future-proofing.

---

## 5. Coverage Map & Gaps

| Area | Covered Tests | Remaining Risks |
| --- | --- | --- |
| Admin (roles, LCATs, audit, AI recommendations, RAG) | Full happy-path CRUD + duplicate/deletion stress | API returns raw IntegrityErrors (improve error handling); no auth/permissions checks implemented. |
| Employees | Happy-path CRUD + invalid data, duplicate email updates | Authentication, authorization, and password reset flows not present. |
| Projects | CRUD + overrides + invalid payloads | No bulk operations; no tests for filtering/sorting beyond limit bounds. |
| Allocations | Assignment & allocation lifecycle + boundary month, overlapping assignments, repeated updates | Cross-user concurrency (locking) not simulated; FTE calculations validated indirectly. |
| Reports | Dashboards, timelines, exports (501 placeholder), parameter bounds | Underlying aggregation correctness relies on stubbed logic; once implemented, add deeper assertions. |
| AI | Chat, recommend, conflicts, forecast, balance, reindex | Real AI integrations are placeholder; once connected to external services, add integration/mocking. |
| Root & Health | Smoke checks | Accepts 404 depending on router configuration; finalize desired behavior. |
| Security | Input sanitation, duplicate conflicts, deletion of referenced entities | Rate limiting, auth, CORS specifics, and penetration testing outside current scope. |

---

## 6. Recommendations & Next Steps

1. **Error Handling Improvements**: Wrap CRUD duplicate/constraint violations in HTTP 409/400 responses to avoid raw 500s; update tests accordingly.
2. **Lifecycle Hooks**: Finalize migration from `@app.on_event` to FastAPI lifespan to eliminate deprecation warnings.
3. **Authentication & Authorization**: Introduce tests once auth features are implemented (JWT issuance, RBAC enforcement, etc.).
4. **Performance / Load Testing**: Consider stress tests around allocation updates and reporting queries when realism increases.
5. **CI Integration**: Add both suites to automated pipelines (e.g., run edge suite nightly, happy-path on each PR).
6. **Documentation**: Keep this overview updated as new modules or security considerations arise (e.g., when AI endpoints move beyond placeholders).

---

## 7. Artifacts

- `tests/conftest.py`: Fixture setup with SQLite, TestClient, password hashing monkeypatch.
- `tests/test_api_happy_path.py`: 11 tests covering user-story flows.
- `tests/test_edge_cases.py`: 27 tests covering validation, security, and robustness.
- `TESTING_SECURITY_OVERVIEW.md`: (this document) living reference for QA/security status.

---

Maintaining this testing discipline ensures regressions or security gaps surface early. As the backend evolves (auth, AI integrations, reporting logic), expand both test suites and revisit this document to reflect the latest assurance posture.

