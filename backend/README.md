# Backend API

FastAPI service for authentication and employee management. It uses MongoDB through Motor and Beanie, validates requests with Pydantic, and protects employee data with expiring JWT Bearer tokens.

## Setup

From PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `.env` with `MONGODB_URL`, `SECRET_KEY`, `SEED_ADMIN_EMAIL`, and `SEED_ADMIN_PASSWORD`. Optional values are `DATABASE_NAME`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and `CORS_ORIGINS`; see `.env.example` for defaults.

The MongoDB user must have access to the database, and the development machine must be allowed by the Atlas network rules. Initialize the admin account and run the service:

```powershell
python scripts\seed_user.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify the service at `http://localhost:8000/health`. OpenAPI UI is at `/docs`, and ReDoc is at `/redoc`.

## Request flow

`POST /auth/login` finds the user by email, verifies the PBKDF2-SHA256 password hash, creates a JWT containing `sub` and `exp`, returns the token, and sets an HttpOnly `token` cookie. Protected routes use the `Authorization: Bearer <token>` header. `get_current_user` decodes the token and loads the user from MongoDB before the route runs.

The FastAPI lifespan calls `init_db()` at startup. Beanie registers the `User` and `Employee` document models and uses the `users` and `employees` collections.

## Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/health` | No | Health check |
| POST | `/auth/login` | No | Login and receive JWT |
| POST | `/auth/logout` | No | Delete auth cookie |
| GET | `/auth/me` | Yes | Current user email and username |
| GET | `/employees` | Yes | Search, filter, sort, and paginate |
| GET | `/employees/stats/summary` | Yes | Totals and grouped breakdowns |
| GET | `/employees/{id}` | Yes | Read one employee |
| POST | `/employees` | Yes | Create employee |
| PUT | `/employees/{id}` | Yes | Update employee |
| DELETE | `/employees/{id}` | Yes | Delete employee |

List query parameters are `page` (default `1`), `limit` (default `10`, maximum `100`), `search`, repeated `department`, and repeated `status`. Search is case-insensitive against name and email. Status values are `Active` and `Inactive`.

Example create/update body:

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "9876543210",
  "department": "Engineering",
  "designation": "Senior Developer",
  "joining_date": "2024-01-15",
  "status": "Active"
}
```

The list response contains `items`, `total`, `page`, `limit`, and `total_pages`. Employee responses also include the MongoDB string `id`, `created_at`, and `updated_at`.

## Validation and errors

- Email must be valid.
- Name, department, and designation cannot be blank.
- Phone must contain 10 to 15 digits, optionally preceded by `+` at the document-model level.
- Joining date cannot be in the future.
- Invalid payloads or IDs return `422`.
- Missing, invalid, or expired tokens return `401`.
- Missing records return `404`.
- Persistence conflicts, including duplicate email errors, return `409`.

## Files and utilities

- `app/main.py`: application, CORS, startup initialization, and health endpoint.
- `app/routers/auth.py`: login, logout, and current-user routes.
- `app/routers/employees.py`: employee CRUD, filtering, pagination, and aggregation.
- `app/core/security.py`: password and JWT helpers.
- `app/dependencies.py`: Bearer-token dependency.
- `app/models/`: MongoDB documents and validation.
- `app/schemas/`: API request/response schemas.
- `scripts/seed_user.py`: creates the configured admin user if absent.
- `scripts/create_user_cli.py`: interactively creates a user.
- `scripts/create_user_noninteractive.py`: creates a user from command-line arguments.
- `check_db.py`: verifies database initialization.

## Commands

```powershell
python check_db.py
python scripts\create_user_cli.py
python scripts\create_user_noninteractive.py user@example.com password username
```

For MongoDB TLS failures, first check the Atlas connection, allowlist, credentials, and Windows clock. The development fallback in `app/db.py` disables TLS certificate verification and must not be used for production.
