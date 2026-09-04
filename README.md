# Mini Employee Management System

Full-stack employee directory with a FastAPI API, MongoDB, and a Next.js App Router interface. The application supports one authenticated management workflow: sign in, inspect dashboard statistics, search and filter employees, and create, view, edit, or delete employee records.

## How the system works

1. The backend starts with Uvicorn and initializes Beanie document models against MongoDB.
2. The seed script creates the first user and stores a PBKDF2-SHA256 password hash.
3. The frontend sends credentials to `POST /auth/login`.
4. The API returns a JWT and also sets an HttpOnly `token` cookie. The frontend stores the returned JWT in `localStorage` for API `Authorization` headers.
5. Every employee request is decoded and checked by `get_current_user` before MongoDB work is performed.
6. The frontend renders the JSON responses as dashboard cards, charts, tables, responsive cards, and forms.

## Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS 4
- Backend: Python, FastAPI, Pydantic, Uvicorn
- Persistence: MongoDB Atlas, Motor, Beanie ODM
- Authentication: JWT with PyJWT and PBKDF2-SHA256 with Passlib

## Features

- Email/password login and logout
- JWT-protected API and authenticated dashboard workflow
- Employee CRUD with server and client validation
- Search by employee name or email
- Multi-select department and status filters
- Server-side pagination with a default page size of 10 and maximum of 100
- Dashboard totals for all, active, and inactive employees
- Department and designation distributions
- Duplicate-email conflict handling
- Responsive desktop table and mobile employee cards
- Loading overlays, inline errors, delete confirmation, and unsaved-form discard confirmation
- FastAPI Swagger and ReDoc documentation

## Prerequisites

- Python 3.10 or newer
- Node.js and npm
- A reachable MongoDB Atlas cluster (or compatible MongoDB server)
- A MongoDB network-access rule allowing the development machine

## Setup on Windows

Open two PowerShell terminals from the repository root.

### 1. Configure and start the backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env`:

```dotenv
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=employee_management
SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=90
CORS_ORIGINS=https://emp-management-app-frontend.vercel.app
SEED_ADMIN_EMAIL=admin@example.com
SEED_ADMIN_PASSWORD=change-this-password
```

Seed the first user once, then launch the API:

```powershell
python scripts\seed_user.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check `http://localhost:8000/health`. Interactive API documentation is available at `http://localhost:8000/docs`; alternative ReDoc documentation is at `/redoc`.

### 2. Configure and start the frontend

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

The browser application is at `http://localhost:3000`. The deployed API is `https://emp-management-app-backend.onrender.com`:

```dotenv
NEXT_PUBLIC_API_BASE_URL=https://emp-management-app-backend.onrender.com
```

For a production-style frontend run `npm run build`, then `npm run start`.

## Environment variables

| Variable | Location | Purpose |
| --- | --- | --- |
| `MONGODB_URL` | backend | MongoDB connection string; required |
| `DATABASE_NAME` | backend | Database name; defaults to `employee_management` |
| `SECRET_KEY` | backend | JWT signing secret; required and must be private |
| `JWT_ALGORITHM` | backend | JWT algorithm; defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | backend | Token lifetime; defaults to 90 minutes |
| `CORS_ORIGINS` | backend | Comma-separated allowed frontend origins |
| `SEED_ADMIN_EMAIL` | backend | Email used by the seed script |
| `SEED_ADMIN_PASSWORD` | backend | Password used by the seed script |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | Public base URL for API requests |

## Backend architecture

- `app/main.py`: creates FastAPI, configures CORS, initializes the database during lifespan, registers routers, and exposes `/health`.
- `app/core/config.py`: reads `.env` through Pydantic Settings.
- `app/core/security.py`: hashes/verifies passwords and creates/decodes expiring JWTs.
- `app/db.py`: creates the Motor client and initializes Beanie with `User` and `Employee` documents.
- `app/dependencies.py`: validates Bearer tokens and loads the current user.
- `app/models/`: MongoDB document definitions and field validators.
- `app/schemas/`: request and response contracts.
- `app/routers/`: authentication and employee endpoints.
- `scripts/`: admin seeding and manual user creation utilities.

Employee fields are `name`, `email`, `phone`, `department`, `designation`, `joining_date`, and `status`. Status is exactly `Active` or `Inactive`; joining dates cannot be in the future; phone numbers must contain 10 to 15 digits in the database model. MongoDB collections are `users` and `employees`.

## API reference

Protected endpoints require `Authorization: Bearer <access_token>`.

| Method | Path | Auth | Result |
| --- | --- | --- | --- |
| GET | `/health` | No | `{ "status": "ok" }` |
| POST | `/auth/login` | No | JWT token and sets `token` cookie |
| POST | `/auth/logout` | No | Deletes the `token` cookie; `204` |
| GET | `/auth/me` | Yes | Authenticated email and username |
| GET | `/employees` | Yes | Filtered, paginated employee list |
| GET | `/employees/stats/summary` | Yes | Status, department, and designation counts |
| GET | `/employees/{employee_id}` | Yes | One employee |
| POST | `/employees` | Yes | Creates an employee; `201` |
| PUT | `/employees/{employee_id}` | Yes | Replaces/updates an employee |
| DELETE | `/employees/{employee_id}` | Yes | Deletes an employee; `204` |

`GET /employees` accepts `page` (minimum 1), `limit` (1-100), `search`, repeated `department`, and repeated `status` parameters. Search is case-insensitive across `name` and `email`; department and status filters are exact MongoDB `$in` filters. The response shape is:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "limit": 10,
  "total_pages": 1
}
```

Create and update payload example:

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

Common responses are `401` for missing/invalid/expired authentication, `404` for an unknown employee, `409` for a duplicate email during persistence, and `422` for invalid request data or employee IDs.

## Frontend routes and responsibilities

- `/`: redirects to `/login`.
- `/login`: validates credentials, calls the auth endpoint, saves the JWT, and redirects to `/dashboard`.
- `/dashboard`: calls the summary endpoint and displays totals plus department/designation breakdowns.
- `/employees`: reads URL query state, debounces search by 400 ms, loads filter options and paginated records, and provides view/edit/delete actions.
- `/employees/new`: validates and creates an employee; warns before discarding entered data.
- `/employees/[id]`: loads and displays one employee.
- `/employees/[id]/edit`: loads, validates, and updates one employee.

`lib/api.ts` is a generic authenticated fetch helper with JSON handling and automatic redirect on `401`; several pages also use direct `fetch` calls for page-specific behavior. `components/` contains navigation, buttons, status badges, loading overlays, inputs, and confirmation modals.

## Useful commands

Backend: `python check_db.py`, `python scripts\create_user_cli.py`, and `python scripts\create_user_noninteractive.py <email> <password> [username]`.

Frontend: `npm run lint`, `npm run build`, `npm run dev`, and `npm run start`.

## Troubleshooting and production notes

- If MongoDB startup times out, verify the connection string, Atlas IP allowlist, credentials, and system clock. `app/db.py` has an insecure development-only TLS fallback; do not use that fallback in production.
- CORS must include the exact frontend origin, including its scheme and port.
- API calls use the localStorage token. A `401` response clears it and sends the user to login.
- Use HTTPS in production, set the auth cookie to `secure=True`, use a strong secret, restrict `CORS_ORIGINS`, and avoid exposing secrets in client-side environment variables.
- The included `backend/app.py` is an older Flask hello-world example and is not the application entry point. Run `uvicorn app.main:app`.
