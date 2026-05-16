# Week 2 Assignment - Reflection Answers

## 1. Factor III: Config – Why use .env file? Why not hardcode passwords in code?

Using a .env file keeps sensitive information like usernames, passwords, and database URLs separate from the source code. This file is not committed to Git (added to .gitignore), which improves security. It also allows different configurations for development, staging, and production without changing the code. Hardcoding passwords in code exposes them to anyone who sees your code. The Twelve‑Factor App states that configuration must be read from the environment, not from the code.

## 2. Factor IV: Backing Services – What is the benefit of treating the database as a separate service?

When the database runs in a separate container (e.g., PostgreSQL via Docker), it can be attached as a resource to any environment. If you later move to a managed database like AWS RDS, you only need to change the database URL in the configuration. Using SQLAlchemy ORM makes switching between databases (PostgreSQL to MySQL or SQLite) easier. Treating backing services as attached resources makes scaling and maintenance simpler.

## 3. Factor X: Dev/Prod Parity – How does Docker make development and production environments similar?

Docker Compose uses the same postgres:latest image locally and in production. Running docker-compose up -d works identically on a developer's laptop and on a production server. The operating system, dependencies, library versions, and startup scripts (like seed.sql) are the same. This eliminates the classic "it works on my machine" problem. Development parity means less debugging and fewer surprises during deployment.

## 4. Factor II: Dependencies – Why do we need requirements.txt and a virtual environment?

requirements.txt lists exact library versions (e.g., fastapi==0.136.1). When another developer runs pip install -r requirements.txt, they get exactly the same versions. A virtual environment (venv) isolates these packages from system‑wide Python packages, preventing version conflicts. The Twelve‑Factor App requires explicit declaration and isolation of dependencies.

## 5. Factor VIII: Concurrency – Why use asyncio.gather()? What is sequential vs concurrent?

- Sequential means waiting for one query to finish before starting the next. For 8 queries, total time = sum of each query's duration (e.g., 8 × 0.1s = 0.8s).
- Concurrent (asyncio.gather) means starting all 8 queries at the same time. Total time = duration of the slowest query (e.g., 0.15s).
FastAPI can handle other tasks while waiting for database responses, improving performance. The /overall_counts endpoint without concurrency would be slow; with concurrency it is fast and scalable (Factor VIII: scale out via concurrency).

## 6. Task 1 – What is the role of .env and seed.sql in the Docker database container?

- .env holds database configuration (username, password, database name, port) so that credentials are external and secure.
- seed.sql creates the database tables (customers, orders, products, etc.) and populates them with sample data.
When Docker Compose starts the container, it reads variables from .env and automatically runs seed.sql from the special init directory (/docker-entrypoint-initdb.d/). This ensures every developer gets the same database structure and initial data.