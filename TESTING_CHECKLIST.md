# StaffAlloc - Testing Checklist

Use this checklist to systematically test all features of the StaffAlloc application.

---

## ✅ Pre-Test Setup

- [x] Backend server running on http://localhost:8000
- [x] Frontend server running on http://localhost:5173
- [x] Database seeded with comprehensive test data
- [x] API documentation accessible at http://localhost:8000/api/docs

---

## 🔐 Authentication & Authorization

### Test Cases

- [ ] **TC-AUTH-001**: Login with Admin credentials (admin@staffalloc.com / admin123)
- [ ] **TC-AUTH-002**: Login with PM credentials (david.kim@staffalloc.com / password123)
- [ ] **TC-AUTH-003**: Login with Employee credentials (alex.thompson@staffalloc.com / password123)
- [ ] **TC-AUTH-004**: Login with Director credentials (michael.rodriguez@staffalloc.com / password123)
- [ ] **TC-AUTH-005**: Attempt login with incorrect password (should fail)
- [ ] **TC-AUTH-006**: Verify JWT token is stored after successful login
- [ ] **TC-AUTH-007**: Verify protected routes redirect to login when not authenticated
- [ ] **TC-AUTH-008**: Logout successfully clears session

### Expected Results
- Different roles should see appropriate menu items and permissions
- Invalid credentials should show error message
- Session should persist across page refreshes

---

## 📊 Dashboard Features

### Test Cases

- [ ] **TC-DASH-001**: View portfolio dashboard as Director
  - Should show total projects count (11)
  - Should show total employees count (27)
  - Should display current allocations summary

- [ ] **TC-DASH-002**: View AI recommendations widget
  - Should show 5 recommendations
  - Should display different types (STAFFING, CONFLICT, etc.)
  - Should show status (Pending, Accepted, Dismissed)

- [ ] **TC-DASH-003**: View recent audit logs
  - Should show recent system activities
  - Should display user who performed action
  - Should show timestamps

- [ ] **TC-DASH-004**: View project status distribution
  - 6 Active projects
  - 3 Planning projects
  - 1 On Hold project
  - 1 Closed project

### Expected Results
- All metrics should display correctly
- Charts/graphs should render (if implemented)
- Data should update when underlying data changes

---

## 🏗️ Project Management

### Test Cases

- [ ] **TC-PROJ-001**: List all projects
  - Should display 11 projects
  - Should show project status badges
  - Should display manager names

- [ ] **TC-PROJ-002**: View project details (ECOM-2024)
  - Should show project metadata (client, dates, sprints)
  - Should display assigned team members (5-8 people)
  - Should show manager information

- [ ] **TC-PROJ-003**: Filter projects by status
  - Active filter: 6 projects
  - Planning filter: 3 projects
  - On Hold filter: 1 project
  - Closed filter: 1 project

- [ ] **TC-PROJ-004**: Create new project (as PM/Admin)
  - Fill in project form
  - Assign manager
  - Set start date and sprints
  - Verify project appears in list

- [ ] **TC-PROJ-005**: Edit existing project
  - Change project name or client
  - Update sprint count
  - Verify changes are saved

- [ ] **TC-PROJ-006**: Delete project (should also cascade delete assignments)
  - Delete a test project
  - Verify it's removed from list
  - Verify assignments are also removed

### Expected Results
- All CRUD operations should work smoothly
- Validation errors should display clearly
- Changes should reflect immediately in the UI

---

## 👥 Employee Management

### Test Cases

- [ ] **TC-EMP-001**: List all employees
  - Should display 27 active employees
  - Should show employee names and emails
  - Should indicate system role

- [ ] **TC-EMP-002**: View employee details (Alex Thompson)
  - Should show current project assignments
  - Should display monthly allocation summary
  - Should calculate total FTE percentage

- [ ] **TC-EMP-003**: Verify over-allocation warning
  - View Alex Thompson in December 2024
  - Should show warning/indicator for 220 hours (over 160 standard)
  - Should display which projects cause over-allocation

- [ ] **TC-EMP-004**: View employee timeline
  - Should show allocation trend over time
  - Should display multiple projects in parallel
  - Should indicate capacity utilization

- [ ] **TC-EMP-005**: Create new employee (as Admin)
  - Fill in employee form
  - Set system role
  - Verify employee appears in list

- [ ] **TC-EMP-006**: Edit employee information
  - Update name or email
  - Change system role
  - Verify changes are saved

- [ ] **TC-EMP-007**: Deactivate employee
  - Set employee to inactive
  - Verify they don't appear in active lists
  - Verify historical allocations remain

### Expected Results
- Employee data should display accurately
- Over-allocation warnings should be prominent
- CRUD operations should work for authorized users

---

## 📅 Allocation Management

### Test Cases

- [ ] **TC-ALLOC-001**: View allocation grid for project
  - Select MOBILE-IOS project
  - View allocation grid
  - Should show all team members as rows
  - Should show months as columns

- [ ] **TC-ALLOC-002**: Edit allocation hours (as PM)
  - Click on a cell in allocation grid
  - Change hours (e.g., 80 → 120)
  - Save changes
  - Verify new value persists

- [ ] **TC-ALLOC-003**: Create new assignment
  - Assign employee to project
  - Set role and LCAT
  - Define funded hours
  - Verify assignment appears

- [ ] **TC-ALLOC-004**: View cross-project allocations
  - Select an employee working on multiple projects
  - View their total monthly hours
  - Verify sum across all projects

- [ ] **TC-ALLOC-005**: Check FTE calculation
  - View employee with 160 hours allocated
  - Should show 100% FTE (or 1.0)
  - View employee with 80 hours allocated
  - Should show 50% FTE (or 0.5)

- [ ] **TC-ALLOC-006**: Detect over-allocation
  - Try to allocate more than 160 hours to an employee
  - System should warn or prevent over-allocation
  - Or show AI recommendation for resolution

### Expected Results
- Grid should be interactive and editable
- Calculations should be accurate
- Validation should prevent invalid data

---

## 🤖 AI Features

### Test Cases

- [ ] **TC-AI-001**: View all AI recommendations
  - Navigate to AI recommendations page
  - Should display 5 recommendations
  - Should show different types and statuses

- [ ] **TC-AI-002**: Accept an AI recommendation
  - Select a Pending recommendation
  - Click Accept
  - Status should change to Accepted
  - acted_upon_at timestamp should be set

- [ ] **TC-AI-003**: Reject an AI recommendation
  - Select a Pending recommendation
  - Click Reject
  - Status should change to Rejected

- [ ] **TC-AI-004**: Dismiss an AI recommendation
  - Select a recommendation
  - Click Dismiss
  - Status should change to Dismissed

- [ ] **TC-AI-005**: View conflict resolution recommendation
  - Should highlight Alex Thompson over-allocation
  - Should suggest specific action (reduce DATA-DASH by 60 hours)

- [ ] **TC-AI-006**: View staffing recommendation
  - Should suggest adding specific role to project
  - Should reference project velocity or capacity

### Expected Results
- Recommendations should be actionable
- Status changes should persist
- Context should be clear and helpful

---

## ⚙️ Admin Features

### Test Cases

- [ ] **TC-ADMIN-001**: View all roles
  - Navigate to Admin → Roles
  - Should display 20 roles
  - Should show descriptions

- [ ] **TC-ADMIN-002**: Create new role
  - Click Add Role
  - Enter name and description
  - Verify role appears in list

- [ ] **TC-ADMIN-003**: Edit existing role
  - Select a role
  - Update description
  - Verify changes saved

- [ ] **TC-ADMIN-004**: View all LCATs
  - Navigate to Admin → LCATs
  - Should display 8 labor categories
  - Should show experience levels

- [ ] **TC-ADMIN-005**: Create new LCAT
  - Click Add LCAT
  - Enter name and description
  - Verify LCAT appears in list

- [ ] **TC-ADMIN-006**: View audit logs
  - Navigate to Admin → Audit Logs
  - Should display recent activities
  - Should show user, action, timestamp
  - Should be sortable/filterable

### Expected Results
- Admin functions should only be accessible to Admin role
- Changes to roles/LCATs should reflect in dropdowns immediately
- Audit logs should capture all significant actions

---

## 📈 Reporting Features

### Test Cases

- [ ] **TC-REPORT-001**: View portfolio dashboard
  - Should aggregate data across all projects
  - Should show total hours allocated per month
  - Should display resource utilization metrics

- [ ] **TC-REPORT-002**: View project-specific dashboard
  - Select ECOM-2024
  - Should show team composition
  - Should display hours burned vs. funded
  - Should show sprint progress

- [ ] **TC-REPORT-003**: View employee timeline
  - Select employee
  - Should show allocation history
  - Should display multiple projects over time
  - Should indicate gaps in allocation

- [ ] **TC-REPORT-004**: Export data (if implemented)
  - Click Export button
  - Should download Excel/CSV file
  - Data should be accurate and formatted

### Expected Results
- Reports should load quickly
- Data should be accurate and up-to-date
- Visualizations should be clear and informative

---

## 🔧 Advanced Features

### Test Cases

- [ ] **TC-ADV-001**: Monthly hour overrides
  - View project with override
  - Should show custom hours (e.g., 140 or 176 instead of 160)
  - Should affect FTE calculations

- [ ] **TC-ADV-002**: Multi-project employee view
  - Select employee on 3+ projects
  - Should see all projects listed
  - Should see aggregated hours

- [ ] **TC-ADV-003**: Historical allocations
  - View closed project (WEB-REDESIGN)
  - Should show completed allocations
  - Should show final hours summary

- [ ] **TC-ADV-004**: Future allocations
  - View planning project (CLOUD-INFRA)
  - Should allow creating allocations for future months
  - Should support planning scenarios

### Expected Results
- Advanced features should work seamlessly
- Edge cases should be handled gracefully
- Data integrity should be maintained

---

## 🌐 API Testing

### Test Cases

- [ ] **TC-API-001**: Health check endpoint
  ```bash
  curl http://localhost:8000/health
  ```
  - Should return status: healthy
  - Database: ok
  - LLM service: unavailable (expected)

- [ ] **TC-API-002**: Get all projects
  ```bash
  curl http://localhost:8000/api/v1/projects/
  ```
  - Should return array of 11 projects

- [ ] **TC-API-003**: Get specific project
  ```bash
  curl http://localhost:8000/api/v1/projects/1
  ```
  - Should return project details with manager info

- [ ] **TC-API-004**: Get all employees
  ```bash
  curl http://localhost:8000/api/v1/employees/
  ```
  - Should return array of employees

- [ ] **TC-API-005**: Get AI recommendations
  ```bash
  curl http://localhost:8000/api/v1/admin/recommendations/
  ```
  - Should return 5 recommendations

- [ ] **TC-API-006**: Create project (POST)
  ```bash
  curl -X POST http://localhost:8000/api/v1/projects/ \
    -H "Content-Type: application/json" \
    -d '{"name":"Test Project","code":"TEST-001",...}'
  ```
  - Should create new project and return ID

- [ ] **TC-API-007**: Update allocation (PUT)
  - Should update existing allocation
  - Should return updated data

- [ ] **TC-API-008**: Delete assignment (DELETE)
  - Should remove assignment
  - Should cascade delete related allocations

### Expected Results
- All endpoints should return appropriate status codes
- Validation errors should return 422 with details
- Authentication required endpoints should return 401 if not authenticated

---

## 🐛 Error Handling

### Test Cases

- [ ] **TC-ERR-001**: Invalid project code (duplicate)
  - Try to create project with existing code
  - Should show validation error

- [ ] **TC-ERR-002**: Invalid date range
  - Try to create allocation with invalid month (13)
  - Should reject with error message

- [ ] **TC-ERR-003**: Negative hours
  - Try to set allocation to negative hours
  - Should reject with validation error

- [ ] **TC-ERR-004**: Missing required fields
  - Submit form with missing required fields
  - Should highlight missing fields

- [ ] **TC-ERR-005**: Database connection lost
  - Stop database (for testing)
  - Should show appropriate error message
  - Should not crash application

### Expected Results
- Errors should be user-friendly
- Technical details should be logged but not shown to user
- Application should remain stable

---

## 📱 UI/UX Testing

### Test Cases

- [ ] **TC-UI-001**: Responsive design
  - Test on different screen sizes
  - Mobile, tablet, desktop
  - All features should be accessible

- [ ] **TC-UI-002**: Loading states
  - All data fetches should show loading indicator
  - Should not show stale data

- [ ] **TC-UI-003**: Empty states
  - View project with no assignments
  - Should show helpful empty state message

- [ ] **TC-UI-004**: Form validation
  - All forms should validate on submit
  - Should highlight invalid fields
  - Should show clear error messages

- [ ] **TC-UI-005**: Navigation
  - All menu items should work
  - Breadcrumbs should be accurate
  - Back button should work correctly

### Expected Results
- UI should be intuitive and consistent
- Feedback should be immediate
- Design should follow best practices

---

## 🔒 Security Testing

### Test Cases

- [ ] **TC-SEC-001**: SQL injection attempt
  - Try injecting SQL in search fields
  - Should be sanitized/escaped

- [ ] **TC-SEC-002**: XSS attempt
  - Try injecting JavaScript in text fields
  - Should be escaped/sanitized

- [ ] **TC-SEC-003**: CSRF protection
  - All state-changing requests should have protection
  - Should reject requests without proper tokens

- [ ] **TC-SEC-004**: Role-based access
  - Employee should not access Admin features
  - PM should not access other PM's edit functions
  - Unauthorized access should return 403

- [ ] **TC-SEC-005**: Password security
  - Passwords should be hashed (not plain text)
  - Should meet complexity requirements
  - Should not be visible in logs or responses

### Expected Results
- Security vulnerabilities should not exist
- All user input should be sanitized
- Proper authorization checks should be in place

---

## 🚀 Performance Testing

### Test Cases

- [ ] **TC-PERF-001**: Page load time
  - Dashboard should load in < 2 seconds
  - Large grids should load in < 3 seconds

- [ ] **TC-PERF-002**: API response time
  - Simple queries should return in < 100ms
  - Complex queries should return in < 500ms

- [ ] **TC-PERF-003**: Concurrent users
  - System should handle multiple users
  - Should not have race conditions

- [ ] **TC-PERF-004**: Large dataset handling
  - Add 100+ employees
  - Add 50+ projects
  - Should still perform acceptably

### Expected Results
- Application should be responsive
- No noticeable lag or freezing
- Database queries should be optimized

---

## 📋 Summary

**Total Test Cases**: ~100+  
**Priority**: Focus on Authentication, Project Management, and Allocation Management first

### Testing Progress
- [ ] All Critical Tests Passed
- [ ] All High Priority Tests Passed
- [ ] All Medium Priority Tests Passed
- [ ] All Low Priority Tests Passed

### Issues Found
_(Document any bugs or issues discovered during testing)_

1. 
2. 
3. 

---

## 📝 Notes

- Test data can be reset using: `python seed_data_comprehensive.py`
- API documentation for manual testing: http://localhost:8000/api/docs
- Use browser DevTools Network tab to debug API issues
- Check backend logs for detailed error messages

---

**Last Updated**: November 6, 2025  
**Tester**: _____________  
**Version**: 1.0

