# TVTC Training Portal (Initial Cut)

## Quick start
1) Create virtual env and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2) Run development server:
   ```bash
   uvicorn app.main:app --reload
   ```
3) Open the create course page:
   http://127.0.0.1:8000/hod/courses/new

## Notes
- Defaults to SQLite `app.db`. To use Postgres, define `DATABASE_URL` in `.env`.
- Seeds: add departments manually for now.
