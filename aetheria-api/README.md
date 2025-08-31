# Aetheria Salon AI API

A production-ready FastAPI backend for AI-powered salon management and treatment recommendations.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Async/Await**: Full async support for high performance
- **Structured Logging**: JSON logs with request tracing
- **Type Safety**: Full type hints with Pydantic v2
- **Database**: AsyncPG for PostgreSQL connections
- **Testing**: Pytest with async support
- **Code Quality**: Ruff, Black, and MyPy configured
- **Containerized**: Docker and docker-compose ready

## Quick Start

### Option 1: Using Poetry (Recommended)

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone and setup**:
   ```bash
   cd aetheria-api
   poetry install
   ```

3. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the application**:
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

### Option 2: Using pip

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .[dev]
   ```

3. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

### Option 3: Using Docker

1. **Build and run with docker-compose**:
   ```bash
   docker-compose up --build
   ```

This will start:
- API server on http://localhost:8080
- PostgreSQL database on port 5432
- Redis on port 6379

## Database Setup

### Prerequisites

This API connects to an existing Supabase PostgreSQL database with the following existing tables:
- `customer` - Customer information
- `assessment_session` - Assessment sessions  
- `intake_form` - Client intake forms
- `machine_scan` - Machine scan data
- `machine_metric` - Machine scan metrics

### New Tables

The API adds two new tables via Alembic migrations:
- `plan` - Treatment plans linked to assessment sessions
- `routine_step` - Individual steps in treatment routines

### Running Migrations

1. **Set DATABASE_URL** in your `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

2. **Run the migration**:
   ```bash
   # Install dependencies first
   pip install -e .[dev]
   
   # Run migration
   alembic upgrade head
   ```

3. **Verify tables were created**:
   ```sql
   -- Connect to your database and run:
   SELECT count(*) FROM plan;
   SELECT count(*) FROM routine_step;
   
   -- Check table structure:
   \d plan
   \d routine_step
   ```

### Migration Details

The migration `001_add_plan_routine_step` creates:

**plan table:**
```sql
CREATE TABLE plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID UNIQUE REFERENCES assessment_session(id) ON DELETE CASCADE,
    skin_profile JSONB NOT NULL,
    rationale JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**routine_step table:**
```sql  
CREATE TABLE routine_step (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES plan(id) ON DELETE CASCADE,
    "when" TEXT CHECK ("when" IN ('AM','PM')) NOT NULL,
    step_order INTEGER NOT NULL,
    product_id UUID NULL,
    instructions TEXT NOT NULL,
    day_of_week INTEGER NULL CHECK (day_of_week BETWEEN 0 AND 6)
);
```

### Rollback

To rollback the migration:
```bash
alembic downgrade base
```

## Testing the API

Once the server is running, test the health endpoint:

```bash
curl http://localhost:8080/healthz
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "0.1.0",
  "environment": "dev",
  "database": true
}
```

### Database Sanity Check

After running migrations, verify the new tables:

```sql
-- Check that tables exist and are empty initially
SELECT count(*) FROM plan;           -- Should return 0
SELECT count(*) FROM routine_step;   -- Should return 0

-- Check existing tables are accessible
SELECT count(*) FROM customer;
SELECT count(*) FROM assessment_session;
```

## API Documentation

- **Swagger UI**: http://localhost:8080/docs (dev only)
- **ReDoc**: http://localhost:8080/redoc (dev only)

## Available Endpoints

- `GET /healthz` - Health check
- `POST /api/v1/intake/` - Create client intake (stub)
- `GET /api/v1/intake/{id}` - Get intake by ID (stub)
- `GET /api/v1/machine/` - List machines (stub)
- `POST /api/v1/engine/recommend` - Get treatment recommendations (stub)
- `POST /api/v1/compare/plans` - Compare treatment plans (stub)

## Development Commands

```bash
# Run tests
make test

# Format code
make fmt

# Lint code
make lint

# Run development server
make run

# View all commands
make help
```

## Project Structure

```
aetheria-api/
├── app/
│   ├── core/           # Core functionality (config, logging, db)
│   ├── routers/        # FastAPI route handlers
│   ├── schemas/        # Pydantic models
│   ├── services/       # Business logic
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── tests/              # Test suite
├── docker-compose.yml  # Development environment
├── Dockerfile          # Production container
├── pyproject.toml      # Python project configuration
└── Makefile           # Development commands
```

## Configuration

Environment variables (set in `.env`):

- `DATABASE_URL` - PostgreSQL connection string
- `APP_ENV` - Application environment (dev/prod)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `TZ` - Timezone (default: Asia/Kolkata)
- `API_KEY` - API key for production authentication

## Next Steps

This is a scaffolding with working stubs. The next phases will implement:

1. **Database Models & Migrations** - SQLAlchemy models, Alembic migrations
2. **Business Logic** - Treatment recommendation engine, rules processing
3. **Authentication & Authorization** - JWT tokens, user roles
4. **WhatsApp Integration** - Real WhatsApp API integration
5. **AI/ML Pipeline** - Treatment optimization algorithms
6. **Monitoring & Observability** - Metrics, traces, alerts

## Security

- API key authentication in production
- CORS protection configured
- Request ID tracking for audit trails
- Structured logging for security monitoring
- Input validation with Pydantic

## Performance

- Async database connections with connection pooling
- Structured JSON logging for efficient parsing
- Container-ready for horizontal scaling
- Health checks for load balancer integration
