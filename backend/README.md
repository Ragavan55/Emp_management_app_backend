# Backend API

This FastAPI service powers employee management and authentication.

## Quick start

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in the values.
3. Start MongoDB Atlas and ensure your cluster is reachable.
4. Run the seed script:
   ```bash
   python scripts/seed_user.py
   ```
5. Launch the app:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Auth

- Login at `POST /auth/login`
- Include the token as `Authorization: Bearer <token>`
- All employee routes require authentication
