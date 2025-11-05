### ADR-001: SQLite + SQLAlchemy for Local Persistence

**Status:** Accepted
**Date:** 2025-11-05
**Context:**
The TripSplit application requires a persistent data store for the initial prototype. The architecture prioritizes a "local-first" approach to enable rapid development, offline capabilities (US013), and a zero-dependency setup for developers. The team has familiarity with SQLite from previous lab work, reducing the learning curve. The primary need is for a structured, relational data model to store users, trips, and expenses as outlined in the PRD.

The main forces at play are the need for development speed and simplicity versus the long-term requirement for scalability and high concurrency mentioned in the NFRs. For the MVP, a lightweight, embedded database is highly preferable to a server-based one that would add operational overhead (e.g., running a separate Docker container or service).

**Decision:**
We will use SQLite as the database engine for the prototype, configured in Write-Ahead Logging (WAL) mode to improve read/write concurrency. We will use the SQLAlchemy library as our data access layer, leveraging its ORM for defining models that map to our database schema and its Core expression language for complex queries. Schema changes and versioning will be managed using Alembic. This stack provides a robust, Python-native solution that is file-based, requires no external server, and is exceptionally fast for the low-concurrency environment of a local prototype.

**Consequences:**
- ✅ **Rapid Setup & Development:** No database server installation or configuration is required; the database is a single file, drastically simplifying the local development environment.
- ✅ **Zero Cost:** SQLite is free and open-source, involving no licensing or hosting costs for the development phase.
- ✅ **Excellent Performance:** For a single-user, local application, file-based I/O with SQLite is extremely fast and has very low latency.
- ⚠️ **Limited Write Concurrency:** While WAL mode helps, SQLite is not designed for high-concurrency write operations and will become a bottleneck as the application scales.
- ⚠️ **Lacks Advanced Features:** It lacks the robust feature set of server-based databases like PostgreSQL, such as advanced user roles, replication, and certain complex query types.

**Alternatives Considered:**
- **PostgreSQL:** The likely production target, but it introduces setup and management overhead (Docker, service management) that would slow down initial prototyping.
- **In-memory only:** Provides maximum speed but lacks data persistence across application restarts, making it unsuitable for the core requirements of the application.

**Follow-up Actions:**
- Implement a strict Repository Pattern using SQLAlchemy to abstract all database interactions, ensuring the database engine can be swapped with minimal code changes.
- Create and maintain Alembic migration scripts with the future PostgreSQL migration in mind, avoiding SQLite-specific syntax.

---

### ADR-002: Local AI/RAG with Open-Source Models

**Status:** Accepted
**Date:** 2025-11-05
**Context:**
The TripSplit PRD specifies key AI-driven features, including smart expense categorization (US010) and a RAG-powered chat for querying trip data (US005, US014). A major constraint for the prototype is to avoid dependencies on paid, cloud-based AI services to eliminate costs, ensure data privacy, and maintain the local-first architecture. The solution must be capable of running entirely on a developer's machine without an internet connection.

The challenge is to deliver the required AI functionality without the performance and quality of large-scale commercial models (like GPT-4) and without incurring API costs. The trade-off is between functionality, cost, and model quality. For the MVP, demonstrating the functionality is prioritized over achieving state-of-the-art accuracy.

**Decision:**
We will implement the AI and RAG features using a stack of locally-run, open-source tools. We will use a local LLM server like Ollama or LM Studio to serve open-source models (e.g., Llama 3 8B, Mistral 7B). For the RAG component, we will use an in-process vector database like ChromaDB to store and query embeddings of expense data. An `AIService` within the FastAPI application will orchestrate the process of embedding data, storing it in ChromaDB, and passing user queries with retrieved context to the local LLM. This approach meets all functional requirements with zero cost and complete data privacy.

**Consequences:**
- ✅ **Zero Financial Cost:** Eliminates all API call costs associated with commercial AI services, making development and local usage free.
- ✅ **Complete Data Privacy:** User expense data is never sent to a third-party service, which is a significant security and privacy advantage.
- ✅ **Enables Offline Functionality:** All AI features can function without an internet connection, aligning perfectly with the local-first and offline-capable goals.
- ⚠️ **Lower Model Quality:** The performance and accuracy of local open-source models will likely be inferior to leading commercial models like GPT-4 or Gemini.
- ⚠️ **Hardware Dependency & Latency:** Inference speed is highly dependent on the developer's local hardware (CPU/GPU), and response latency may be higher than cloud APIs.

**Alternatives Considered:**
- **OpenAI / Google Gemini APIs:** Offer superior model quality but introduce cloud dependencies, API costs, and data privacy considerations that conflict with the prototype's goals.
- **No AI:** Would fail to deliver on core product differentiators and functional requirements outlined in Epic 4 of the PRD.

**Follow-up Actions:**
- Create an abstract `LLMAdapter` and `VectorStoreAdapter` to decouple the application logic from the specific implementations (Ollama, ChromaDB).
- Establish a benchmark to evaluate the quality of local models for the specified tasks and define a quality threshold for considering a move to cloud-based models.

---

### ADR-003: FastAPI Monolith with APScheduler for Background Jobs

**Status:** Accepted
**Date:** 2025-11-05
**Context:**
The application requires a mechanism for running asynchronous background tasks that should not block the main API request-response cycle. Key use cases include indexing new expenses into the ChromaDB vector store for the RAG system or generating a large PDF report (US012). The current architecture for the prototype is a single-process FastAPI monolith, as shown in the architecture diagram.

The primary constraint is to keep the architecture as simple as possible for the prototype. Introducing external dependencies like a message broker (e.g., Redis) and separate worker processes would add significant complexity to the local development setup and deployment. The solution must be lightweight and integrate easily within the existing monolithic structure.

**Decision:**
We will use `APScheduler` (Asynchronous Python Scheduler) integrated directly into the FastAPI application process to handle background jobs. We will configure a `BackgroundScheduler` that runs in a separate thread within the main application process. API endpoints that need to trigger a background task will enqueue it using FastAPI's `BackgroundTasks` for immediate, non-blocking tasks, or `APScheduler` for scheduled or more complex jobs. This approach provides the necessary functionality with minimal configuration and no additional infrastructure, perfectly suiting the needs of a self-contained, local-first prototype.

**Consequences:**
- ✅ **Simplicity:** The implementation is trivial, requiring only a few lines of code to integrate into the FastAPI application lifecycle.
- ✅ **No External Dependencies:** Avoids the need to install, configure, and run a separate message broker (like Redis) and a task queue worker (like Celery).
- ✅ **Zero Infrastructure Overhead:** Consumes resources from the main application process, requiring no additional services, containers, or process managers.
- ⚠️ **Limited Scalability:** Jobs compete for CPU and memory with the API server. Heavy or numerous jobs could degrade API performance. This solution does not scale across multiple server instances.
- ⚠️ **Lack of Durability:** Since jobs are scheduled in-memory, they are lost if the application process crashes or restarts. There is no built-in retry mechanism or persistent queue.

**Alternatives Considered:**
- **Celery with Redis/RabbitMQ:** The industry-standard for robust, distributed task queues. It is powerful but considered overkill for the prototype due to its complexity and infrastructure requirements.
- **Separate Worker Process:** A custom Python script could poll the database for jobs. This is more durable than APScheduler but adds complexity in process management and deployment.

**Follow-up Actions:**
- Abstract the job enqueuing logic into a dedicated service to make it easier to swap out the backend from APScheduler to Celery in the future.
- Define clear performance metrics (e.g., API response time degradation, job queue length) that will trigger the migration to a more robust, distributed task queue system.