# Cloud File Storage Service

A secure, containerized REST API for storing and managing user files, built with **FastAPI, PostgreSQL, SQLAlchemy, Docker, and JWT authentication**.

The project focuses on backend architecture, authentication and authorization, database management, automated testing, continuous integration, and cloud deployment.

## Problem

The goal of this project was to build a backend system where multiple users can securely upload and manage their files while ensuring that users cannot access files belonging to someone else.

The system supports:

* User registration and authentication
* Secure password hashing
* JWT-based authorization
* File uploads with unique internal filenames
* File metadata persistence
* Ownership-based access control
* File listing, downloading, renaming, and deletion
* Database schema migrations
* Automated testing
* Containerized development
* Continuous integration
* Cloud deployment

## Features

### Authentication & Security

* User registration
* User login
* Secure password hashing using `pwdlib`
* JWT access tokens
* Protected API routes
* User-specific file ownership
* Authorization checks preventing cross-user file access
* Environment-based secret management
* Centralized exception handling

### File Management

Authenticated users can:

* Upload files
* View their uploaded files
* Download files
* Rename files
* Delete files

Uploaded files receive a UUID-based internal filename to prevent filename collisions.

For example:

```text
Original filename:
resume.pdf

Stored filename:
550e8400-e29b-41d4-a716-446655440000-resume.pdf
```

The original filename remains available to the user while the generated filename is used internally.

## Architecture

The application follows a layered backend architecture:

```text
Client
   ↓
FastAPI Router
   ↓
Service Layer
   ↓
Repository Layer
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

Each layer has a separate responsibility:

* **Routers** handle HTTP requests and responses.
* **Services** contain business rules and application workflows.
* **Repositories** handle database operations.
* **Schemas** validate request and response data.
* **Models** represent database entities.
* **Core** contains configuration, authentication, security, logging, and exception handling.

This separation keeps HTTP handling, business logic, and database access independent and makes the application easier to maintain and test.

## Project Structure

```text
cloud-file-storage-service/
│
├── .github/
│   └── workflows/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── core/
│   ├── database/
│   ├── exceptions/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   └── services/
│
├── storage/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## Technology Stack

* **Python**
* **FastAPI**
* **PostgreSQL**
* **SQLAlchemy**
* **Pydantic**
* **Alembic**
* **JWT / python-jose**
* **pwdlib**
* **Docker**
* **Docker Compose**
* **PyTest**
* **GitHub Actions**
* **Railway**

## API Functionality

### Users

```text
POST /users/register
POST /users/login
GET  /users/me
```

### Files

```text
POST   /files/upload
GET    /files
GET    /files/{file_id}/download
PATCH  /files/{file_id}/rename
DELETE /files/{file_id}
```

### System

```text
GET /health
```

Interactive API documentation is available through FastAPI Swagger UI.

## Automated Testing

The project includes an automated PyTest suite covering the main API workflows.

Tests include:

* Health endpoint
* User registration
* Duplicate registration rejection
* Successful login
* Invalid password rejection
* Valid JWT authentication
* Missing authentication
* Invalid JWT rejection
* File upload
* File listing
* File rename
* File download
* File deletion
* Cross-user ownership protection

The test environment is isolated from development data.

```text
Development
├── PostgreSQL development database
└── storage/

Testing
├── PostgreSQL test database
└── test_storage/
```

Temporary test file storage is automatically removed after the test session.

Run the complete test suite with:

```bash
pytest -v
```

## Continuous Integration

The repository uses **GitHub Actions** to automatically run the test suite when code is pushed to the repository.

The CI workflow:

```text
Git Push
   ↓
GitHub Actions
   ↓
Start PostgreSQL
   ↓
Set up Python
   ↓
Install dependencies
   ↓
Run PyTest
   ↓
Pass / Fail
```

This provides automated regression checking independently of the local development environment.

## Docker

The FastAPI application and PostgreSQL database can run using Docker Compose.

Start the application with:

```bash
docker compose up --build
```

The local API is available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Stop the containers with:

```bash
docker compose down
```

## Database Migrations

Database schema changes are managed using **Alembic**.

Apply all migrations with:

```bash
alembic upgrade head
```

The migration history can initialize the application schema from a fresh PostgreSQL database.

This became particularly important during cloud deployment. The original local PostgreSQL database contained tables that existed before Alembic was introduced, which initially hid an incomplete migration. Deploying against a fresh Railway PostgreSQL database exposed the problem, and the migration chain was corrected so the database can now be reproduced from an empty state.

## Cloud Deployment

The backend is deployed on **Railway**.

The production architecture is:

```text
GitHub
   ↓
Railway
   │
   ├── FastAPI Container
   │
   └── PostgreSQL
```

Railway builds the FastAPI service from the project's Dockerfile.

Production database credentials and application secrets are supplied through environment variables rather than being committed to the repository.

### Live API

https://cloudstorage-production-e1f7.up.railway.app

### Swagger Documentation

https://cloudstorage-production-e1f7.up.railway.app/docs

## Configuration

Application configuration is managed centrally using Pydantic settings and environment variables.

Required variables include:

```env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=

SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

STORAGE_PATH=storage
```

The `.env` file containing local credentials and secrets is excluded from Git.

## Engineering Decisions

### Unique Internal Filenames

Users may upload files with identical names.

Using the original filename directly could cause one upload to overwrite another.

The backend therefore generates a UUID-based internal filename:

```text
resume.pdf
        ↓
UUID generated
        ↓
550e8400-e29b-41d4-a716-446655440000-resume.pdf
```

The original name and stored name are maintained separately.

### Ownership-Based Authorization

Authentication answers:

> Who is making the request?

Authorization answers:

> Is this user allowed to access this resource?

Every protected file operation checks the authenticated user's ID against the file's `owner_id`.

This prevents one authenticated user from downloading, renaming, or deleting another user's files.

### Service and Repository Layers

Database queries are isolated in repository modules.

Business rules and application workflows are handled by services.

For example:

```text
Router
   ↓
"Rename this file"

Service
   ↓
Validate request
Check ownership

Repository
   ↓
Update database
```

This keeps database-specific code separate from application logic.

### Centralized Configuration

Application modules access configuration through one centralized settings object rather than reading environment variables independently.

This allows the same application code to run across:

```text
Local development
Docker
PyTest
GitHub Actions
Railway
```

with environment-specific configuration supplied externally.

### Global Exception Handling

The application uses custom exceptions and centralized FastAPI exception handlers.

This provides consistent API errors for cases such as:

* Invalid credentials
* Duplicate users
* Missing files
* Permission failures
* Invalid filenames

### Logging

Important application events are recorded using Python logging, including:

* User registration
* Successful login
* Failed login attempts
* File uploads
* File renames
* File deletion
* Unauthorized file access attempts
* Unexpected file-operation failures

Sensitive values such as passwords, JWTs, and secret keys are not intentionally written to application logs.

## Testing Strategy

Automated tests use a dedicated PostgreSQL test database rather than the development database.

File uploads created during tests use separate temporary storage.

This prevents tests from modifying development users, metadata, or uploaded files.

The same test suite also runs through GitHub Actions, providing an additional clean environment outside the developer's machine.

## Current Limitation

The deployed application currently stores uploaded file binaries on the application's filesystem.

This is sufficient for demonstrating the API and file-management workflow, but container-local filesystem storage should not be treated as durable production object storage.

A future infrastructure improvement is to store file objects using a service such as **Amazon S3**, while PostgreSQL continues storing metadata and ownership information.

## Development Journey

This project began as a basic FastAPI file-storage API and gradually evolved into a more structured backend software-engineering project.

The development process included:

* Designing REST endpoints
* Integrating PostgreSQL
* Modeling relational data with SQLAlchemy
* Implementing password security
* Building JWT authentication
* Debugging authorization and ownership behavior
* Introducing UUID-based file storage
* Adding Alembic database migrations
* Separating routers, services, and repositories
* Centralizing configuration
* Adding response schemas
* Implementing custom exception handling
* Adding structured logging
* Building automated tests
* Isolating testing infrastructure
* Containerizing the API and database
* Building a GitHub Actions CI workflow
* Deploying the application and PostgreSQL to Railway
* Debugging differences between local and production environments

## What I Learned

One of the most important lessons from the project was that making software work locally is only part of building a reliable system.

Testing and deployment exposed assumptions that were invisible during initial development.

For example, the local database already contained tables created before Alembic was introduced. This allowed the application to work locally even though the initial migration did not fully reproduce the schema. Deploying against a completely fresh PostgreSQL database exposed that issue and required correcting the migration history.

The project also reinforced the importance of:

* Separation of concerns
* Authentication versus authorization
* Reproducible environments
* Database migration discipline
* Automated regression testing
* Environment-based configuration
* Debugging from logs and observed system behavior rather than assumptions

## Future Improvements

Potential next steps include:

* Amazon S3 object storage
* Durable cloud file storage
* File sharing
* Rate limiting
* Background processing
* File scanning
* Improved monitoring and observability
* Frontend client

## Security Notes

* Passwords are stored as hashes rather than plaintext.
* JWT signing secrets are supplied through environment variables.
* Database credentials are not committed to Git.
* `.env` files are excluded through `.gitignore`.
* File access is restricted by ownership.
* Test data is isolated from development and production data.
