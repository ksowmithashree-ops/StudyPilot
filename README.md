# StudyPilot

AI-powered adaptive study planner for students. Generate a realistic daily plan from subjects, topics, deadlines, difficulty, progress and available time. Missed sessions reschedule automatically. Plans never exceed available study hours.

## Stack

- Frontend: React, Vite, JavaScript, Tailwind CSS, Recharts, Lucide
- Backend: Python Flask
- Database: SQLite
- AI: Gemini when `GEMINI_API_KEY` is set, otherwise a local heuristic planner and chat fallback

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

API runs at `http://127.0.0.1:5000`. Demo data for student **Alex** is seeded on first launch.

Optional: copy `.env.example` to `backend/.env` and set `GEMINI_API_KEY`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite runs at `http://127.0.0.1:5173` and proxies `/api` to Flask.

## Demo reset

- Landing → **Get Started / Try Demo**
- Settings → **Reset demo data**
- `POST /api/demo/reset`

Seeded scenario: DBMS midterm in 5 days, Normalization at 18%, 3 hours/day available.

## Tests

```bash
cd backend
.venv\Scripts\activate
pytest
```

## Hackathon demo flow

See [PRESENTATION.md](PRESENTATION.md).
