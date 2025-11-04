# Capstone Project Ideas - AI Navigator Team

This document contains original project ideas for the AI-Enabled Software Engineering capstone. All ideas are designed to be achievable in one day by a team of three using AI assistance, while meeting all core requirements and offering potential for extensions.

---

## 🧳 Travel-Related Project

### 1. **TripSplit: Group Travel Expense Manager**

**Description:** A collaborative expense tracking application specifically designed for group travel. Travelers can create trips, add participants, log expenses, and automatically calculate who owes whom at the end of the trip.

**Core Features:**
- Create and manage trips with multiple participants
- Add expenses with category, amount, payer, and split method (equal, percentage, custom)
- View real-time balance summary showing who owes whom
- Generate settlement recommendations (minimize number of transactions)
- Export expense reports

**Why This Works:**
- Clear CRUD operations (Trips, Participants, Expenses, Settlements)
- Natural database relationships (many-to-many)
- Simple but useful UI (forms, lists, summary dashboard)
- Real-world problem many can relate to

**Extension Possibilities (Bonus):**
- RAG: Chat interface to query expenses ("How much did we spend on food?")
- Agent: Smart categorization of expenses using AI
- Receipt photo upload and OCR parsing
- Currency conversion integration
- Split by item (restaurant bills)

---

## 🏢 Business & Productivity Projects

### 2. **MeetingMind: AI-Enhanced Meeting Manager**

**Description:** A meeting management system that helps teams organize meetings, track action items, and ensure follow-through. Users can create meetings, add attendees, document decisions, and assign action items.

**Core Features:**
- Schedule and manage meetings with agenda items
- Add participants and track attendance
- Create and assign action items with due dates and owners
- Track action item completion status
- View dashboard of upcoming meetings and pending action items
- Generate meeting summaries

**Why This Works:**
- Relatable to everyone in business/academic settings
- Rich data model (Meetings, Participants, AgendaItems, ActionItems)
- Multiple views (calendar, todo list, reports)
- Clear demonstration of CRUD operations

**Extension Possibilities (Bonus):**
- RAG: Upload meeting transcripts and query with natural language
- Agent: Automatically extract action items from meeting notes
- Integration with calendar APIs
- Email notifications for action items
- Recurring meeting templates

---

### 3. **SkillTracker: Employee Training & Skills Management**

**Description:** An internal HR tool for managing employee skills, training programs, and certification tracking. Helps organizations identify skill gaps and plan professional development.

**Core Features:**
- Manage employee profiles with current skills and proficiency levels
- Create and track training programs and courses
- Assign training to employees with completion tracking
- Track certifications and renewal dates
- Generate skills gap reports by department
- View employee development progress

**Why This Works:**
- Enterprise-relevant use case
- Complex relationships (employees, skills, courses, certifications)
- Multiple user perspectives (employees, managers, HR)
- Reporting capabilities showcase backend logic

**Extension Possibilities (Bonus):**
- Agent: Recommend training based on career goals and skill gaps
- RAG: Query training catalog with natural language
- Certificate expiration notifications
- Skills matching for internal job postings
- Learning path recommendations

---

### 4. **ProjectPulse: Freelancer Project & Time Tracker**

**Description:** A project management tool for freelancers to track multiple client projects, log time entries, calculate billable hours, and generate invoices.

**Core Features:**
- Manage multiple clients and projects
- Log time entries with project, task description, and duration
- Set hourly rates per project or client
- View time logs and calculate billable amounts
- Generate simple invoice summaries
- Dashboard showing active projects and weekly hours

**Why This Works:**
- Clear business value and real-world application
- Good balance of complexity (Projects, Clients, TimeEntries, Invoices)
- Calculation logic (hours × rates) demonstrates backend processing
- Appeals to many students who may freelance

**Extension Possibilities (Bonus):**
- RAG: Natural language query of time logs ("How many hours on client X last month?")
- Agent: Suggest project estimates based on historical data
- Export invoices as PDF
- Calendar integration
- Expense tracking

---

## 🏥 Health & Wellness Projects

### 5. **WellnessLog: Personal Health & Habit Tracker**

**Description:** A comprehensive wellness tracking application where users can log daily habits (exercise, water intake, sleep, mood) and view trends over time to improve their health.

**Core Features:**
- Create custom trackable habits/metrics
- Daily logging interface for multiple metrics
- View historical data and trends with charts
- Set goals and track progress
- Weekly/monthly summary reports
- Dashboard with current streaks

**Why This Works:**
- Personal and engaging for demo
- Time-series data provides interesting backend challenges
- Visual data representation works well in React
- Flexible data model (users, habits, logs, goals)

**Extension Possibilities (Bonus):**
- Agent: Provide personalized health insights and recommendations
- RAG: Chat with your health data ("When did I last exercise 5 days in a row?")
- Trend analysis and correlations
- Reminder notifications
- Integration with fitness APIs

---

## 🎓 Education & Learning Projects

### 6. **StudyBuddy: Collaborative Study Session Planner**

**Description:** A platform for students to organize study groups, share resources, schedule sessions, and track study progress for different courses or subjects.

**Core Features:**
- Create study groups for different courses/subjects
- Schedule study sessions with location and topic
- Add group members and track participation
- Share resources (links, notes, descriptions)
- Track study hours per subject
- View upcoming sessions and group activity

**Why This Works:**
- Highly relatable to student audience
- Social/collaborative aspect adds interest
- Multiple entities (Groups, Sessions, Members, Resources)
- Calendar and scheduling features

**Extension Possibilities (Bonus):**
- RAG: Search through shared study materials
- Agent: Suggest study schedules based on exam dates
- Resource recommendations
- Quiz generation from study materials
- Virtual study room integration

---

### 7. **CodeReview: Peer Programming Assignment Manager**

**Description:** A lightweight code review platform for educational settings where students can submit programming assignments, request peer reviews, and provide feedback.

**Core Features:**
- Create courses and assignments
- Submit code solutions (via URL or text)
- Request reviews from peers
- Provide structured feedback (comments, ratings)
- Track review completion and feedback received
- View assignment submissions and review status

**Why This Works:**
- Meta: building a tool for software engineering course
- Version control and code review concepts are familiar
- Clear workflow (submit → review → feedback)
- Good data relationships

**Extension Possibilities (Bonus):**
- Agent: Automated code quality checks
- RAG: Search through previous assignments and feedback
- Syntax highlighting
- GitHub integration
- Plagiarism detection

---

## 🏠 Lifestyle & Home Management Projects

### 8. **HomeInventory: Smart Household Item Manager**

**Description:** A home inventory system to track household items, their locations, quantities, purchase dates, and warranty information. Useful for insurance, moving, or just staying organized.

**Core Features:**
- Organize items by room/location
- Track item details (name, category, purchase date, value, warranty)
- Upload item photos (optional for MVP)
- Search and filter inventory
- Generate inventory reports (total value, items by room)
- Track warranties and expiration dates

**Why This Works:**
- Universal appeal (everyone has stuff)
- Hierarchical organization (home → rooms → items)
- Search and filtering showcase backend capabilities
- Practical real-world use case

**Extension Possibilities (Bonus):**
- RAG: Natural language inventory search
- Agent: Predict when to reorder consumables
- Barcode scanning for adding items
- Insurance document generation
- Moving checklist integration

---

## 📊 Recommendation Matrix

| Project | Complexity | Appeal | Demo Impact | Extension Potential | Time Feasibility |
|---------|-----------|---------|-------------|-------------------|------------------|
| TripSplit | Medium | High | High | Excellent | ⭐⭐⭐⭐⭐ |
| MeetingMind | Medium | High | Medium | Excellent | ⭐⭐⭐⭐⭐ |
| SkillTracker | Medium-High | Medium | High | Good | ⭐⭐⭐⭐ |
| ProjectPulse | Medium | High | Medium | Good | ⭐⭐⭐⭐⭐ |
| WellnessLog | Medium | High | High | Excellent | ⭐⭐⭐⭐ |
| StudyBuddy | Medium | High | Medium | Good | ⭐⭐⭐⭐⭐ |
| CodeReview | Medium-High | Medium | High | Excellent | ⭐⭐⭐⭐ |
| HomeInventory | Low-Medium | Medium | Medium | Good | ⭐⭐⭐⭐⭐ |

---

## 💡 Selection Criteria

When choosing your project, consider:

1. **Database Complexity:** Need at least 3-4 related tables for good architecture demo
2. **CRUD Coverage:** Ensure all Create, Read, Update, Delete operations are needed
3. **UI Interest:** Visual elements (lists, dashboards, forms) make better demos
4. **Relatability:** Projects the audience understands perform better in presentations
5. **Extension Path:** Clear RAG/Agent applications for bonus points
6. **Team Division:** Can three people work in parallel (one on backend, one on frontend, one on documentation)?

---

## 🎯 Top Recommendations

Based on one-day feasibility and impact:

1. **TripSplit** - Great demo, relatable, clear calculations showcase backend logic
2. **ProjectPulse** - Appeals to freelancers, clear business value, time tracking is engaging
3. **StudyBuddy** - Relatable to students, collaborative features interesting, good social component

All three have excellent extension possibilities for RAG and Agents if time permits.
