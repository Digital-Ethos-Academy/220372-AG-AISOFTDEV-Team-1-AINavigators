#  Capstone Project: AI-Driven Software Engineering

Welcome to the final project for the AI-Driven Software Engineering Program! This two-day capstone is your opportunity to synthesize all the skills you've acquired over the past eight days. You will apply AI-assisted techniques across the entire software development lifecycle to build a complete, functional application from the ground up.

---

## 🎯 Project Goal

The primary goal of this capstone is to **build and present a working prototype of a software application, demonstrating the integration of Generative AI at every phase of the SDLC**. You will act as a full-stack developer, using AI as your co-pilot for planning, architecture, coding, testing, and documentation.

---

##  deliverables Checklist

Your final submission must include the following components. You will use AI assistance to generate and refine each of these artifacts.

* **Documentation:**
    * `Product Requirements Document (PRD)` generated from a high-level idea.
    * `Architecture Document` including auto-generated UML diagrams (e.g., Component or Sequence diagrams).
    * `Architecture Decision Records (ADR)` including auto-generated technical decisions with their justifications.
* **Backend Application:**
    * A complete REST API project using **Python and FastAPI**.
    * An AI-generated database schema (e.g., `schema.sql`).
    * A suite of **unit tests** generated with AI assistance.
    * A report or list of identified **security vulnerabilities**.
* **Frontend Application:**
    * A **React** frontend that interacts with your backend API.
    * At least one key component generated from a **design screenshot or mockup**.
* **Final Presentation:**
    * A **10-15 minute presentation** summarizing your project.
    * A **live demo** of your fully working front-end and back-end application.
* **AI Code:**
    * A **ipynb or py file(s)** containing the code you used to generate your artifacts.

---


---

## 💡 Suggested Project Ideas

You are encouraged to submit a project proposal for a tool of your choice. To get you started, here are some sample projects that align well with the course content:

* **AI-Powered Requirement Analyzer:** An application that takes a vague problem statement and generates a detailed PRD, user stories, and acceptance criteria.
* **Automated Test Case Assistant:** A tool that reads a Python function or API endpoint and generates a comprehensive suite of `pytest` unit tests, including edge cases.
* **CI/CD Pipeline Summarizer:** An application that ingests CI/CD logs and generates a human-readable summary of build successes, failures, and test results.
* **RAG-Powered Documentation Chatbot:** A chatbot with a RAG backend that can answer questions about a specific codebase or technical document.

---

## 🗓️ Timeline & Schedule

### **Day 9: Build Day (Focus: Implementation)**

This day is dedicated entirely to hands-on development. Follow the workflow below to build your application.

* **Morning (9:00 AM - 12:15 PM):** Project Planning, Architecture, and Backend Development.
* **Afternoon (1:15 PM - 4:30 PM):** Quality Assurance, Frontend Development, and Integration.

### **Day 10: Demo Day (Focus: Presentation & Showcase)**

* **Morning (9:00 AM - 12:00 PM): Final Preparations**
    * Finalize any remaining code and integration tasks.
    * Thoroughly test your application for the live demo.
    * Prepare your 10-15 minute presentation slides.
* **Afternoon (1:00 PM - 4:30 PM): Capstone Project Demos**
    * Each student/team will present their project to the class.
    * Celebrate your hard work and see what your peers have built!

---

## 🚀 Step-by-Step Workflow

This is your roadmap for Day 9. Use this workflow to ensure you touch on all the key skills learned during the course.

### **Phase 1: AI as Product Manager (Planning & Requirements)**

* **Goal:** Create a comprehensive PRD.
* **Action:**
    1.  Start with a high-level idea for your application.
    2.  Use an LLM to brainstorm features, user personas, and user stories with acceptance criteria (as you did on **Day 1**).
    3.  Provide the brainstormed content and a template to the LLM to generate a formal `prd.md` file.
    * **Artifact:** `prd.md`

### **Phase 2: AI as Architect (Design & Architecture)**

* **Goal:** Define your application's architecture and data structure.
* **Action:**
    1.  Feed your `prd.md` to an LLM.
    2.  Prompt it to generate a high-level system architecture. Ask for **diagrams-as-code (PlantUML)** for your architecture document (as you did on **Day 2**).
    3.  Prompt it to generate the `CREATE TABLE` statements for your database schema.
    * **Artifacts:** `architecture.md` (with diagrams), `schema.sql`

### **Phase 3: AI as Backend Developer (Coding)**

* **Goal:** Build a functional FastAPI backend.
* **Action:**
    1.  Provide your `schema.sql` to an LLM.
    2.  Prompt it to generate Pydantic and SQLAlchemy models.
    3.  Prompt it to generate the FastAPI application boilerplate with full CRUD endpoints for your models (as you did on **Day 3**).
    4.  Integrate the generated code and connect it to a live SQLite database.
    * **Artifacts:** `main.py`, `onboarding.db` (or similar)

### **Phase 4: AI as QA Engineer (Testing & Security)**

* **Goal:** Ensure your backend is robust and secure.
* **Action:**
    1.  Provide your `main.py` source code to an LLM.
    2.  Prompt it to generate a suite of `pytest` unit tests for your API, including "happy path" and edge cases (as you did on **Day 4**).
    3.  Prompt it to act as a security expert and identify potential vulnerabilities in your code (e.g., SQL injection, lack of input validation).
    * **Artifacts:** `test_main.py`, `security_review.md`

### **Phase 5: AI as Frontend Developer (UI/UX)**

* **Goal:** Create a user interface for your application.
* **Action:**
    1.  Create a simple wireframe or find a screenshot of a UI you like.
    2.  Use a **vision-capable LLM** to generate a React component with Tailwind CSS from that image (as you did on **Day 7/8**).
    3.  Prompt a text-based LLM to create additional components as needed.
    * **Artifact:** `src/App.js` and other React components.

---

## 🎤 Presentation Guidelines

Your final presentation should be a concise and engaging overview of your project. Please include the following:

1.  **Project Title & Goal:** What did you build and why?
2.  **AI-Assisted Workflow:** Showcase how you used GenAI in **at least three distinct phases** of the SDLC.
    * Show a "before" (the prompt) and "after" (the generated artifact).
3.  **Technical Architecture:** Briefly explain your system design.
4.  **Live Demo:** A walkthrough of your working application. This is the most important part!
5.  **Challenges & Learnings:** What was challenging? What were your key takeaways from the project?

---

## 📝 Submission & Evaluation

* **Submission:** Please push your complete project, including all artifacts and source code, to a GitHub repository and submit the link.
* **Evaluation Criteria:** Projects will be evaluated based on:
    1.  **Completeness:** Were all required deliverables submitted?
    2.  **Functionality:** Does the application work as demonstrated?
    3.  **Innovative Use of AI:** How effectively and creatively did you leverage GenAI across the SDLC?
    4.  **Documentation Quality:** Is the PRD and architecture well-defined?
    5.  **Presentation Clarity:** Was the demo and explanation clear and professional?

Good luck, and have fun building! The instructional team is here to support you.