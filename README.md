# Mini Employee Management System

## Overview

This project is a full-stack employee management application with a FastAPI backend, a Next.js frontend, and MongoDB Atlas persistence. It includes authentication, employee CRUD, filtering, pagination, dashboard summaries, and a user-friendly admin interface.

## Tech stack

- Frontend: Next.js 16, React 19, Tailwind CSS
- Backend: FastAPI, Python 3.13, Pydantic, Beanie Motor
- Database: MongoDB Atlas
- Auth: JWT + bcrypt password hashing
- Version control: Git

## Features implemented

- JWT-based admin login
- Protected employee routes
- Employee create, read, update, delete
- Search and filtering with pagination
- Dashboard summary cards
- MongoDB indexing and validation
- CORS and global error handling

## Local setup

### Backend

1. Open a terminal in `backend/`.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and update the values.
5. Seed the admin account:
   ```bash
   python scripts/seed_user.py
   ```
6. Start the API:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. Open a terminal in `frontend/`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy `.env.local.example` to `.env.local` and set the API URL.
4. Start the app:
   ```bash
   npm run dev
   ```
5. Open http://localhost:3000

## Environment variables reference

### Backend

- `MONGODB_URL`
- `DATABASE_NAME`
- `SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CORS_ORIGINS`
- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_PASSWORD`

### Frontend

- `NEXT_PUBLIC_API_BASE_URL`

## Project structure

- `backend/` — FastAPI app, MongoDB access, auth, employee APIs
- `frontend/` — Next.js app, dashboard, list pages, forms, route protection
- `README.md` — setup and API documentation

## API documentation

The API is documented through FastAPI Swagger at `/docs` on the backend.

### Auth endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/auth/login` | No | Email/password login; returns JWT |

### Employee endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/employees` | Yes | List employees with search, filters, pagination |
| GET | `/employees/{id}` | Yes | Retrieve a single employee |
| POST | `/employees` | Yes | Create an employee |
| PUT | `/employees/{id}` | Yes | Update an employee |
| DELETE | `/employees/{id}` | Yes | Delete an employee |
| GET | `/employees/stats/summary` | Yes | Returns totals by status |
| GET | `/health` | No | Basic API uptime check |

Query parameters for list route:

- `page` (default `1`)
- `limit` (default `10`)
- `search` (partial match on name or email)
- `department` (exact match)
- `status` (exact match: `Active` or `Inactive`)

Response for list route:

```json
{
  "items": [],
  "total": 47,
  "page": 1,
  "limit": 10,
  "total_pages": 5
}
```

## Database setup

- MongoDB Atlas cluster hosts the database.
- Collections used: `employees` and `users`.
- Indexes include a unique email index on both documents and supporting indexes for department/status filtering.

## Deployment details

- Frontend: deploy on Vercel or any Node hosting that supports Next.js.
- Backend: deploy on Render, Railway, or any Python/FastAPI host.
- Database: MongoDB Atlas cluster.
- Required deployment env configuration: update `CORS_ORIGINS`, `MONGODB_URL`, `SECRET_KEY`, and frontend `NEXT_PUBLIC_API_BASE_URL`.

## Known limitations

- The assignment is implemented as a working local demo with JWT auth and CRUD flows.
- Cookie-based auth would be a stronger production option; this version uses token storage in the browser for simplicity and notes the tradeoff.
