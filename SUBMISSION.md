# Week 4 Lab — Submission

**Student:** Mingjing Zhang
**Course:** CSE552 — Full Stack Course
**Lab:** Week 4 — Databases & Full Stack Integration
**Date:** 2026-05-28

---

## 1. GitHub Repositories

| Repo | URL |
|---|---|
| Backend (FastAPI + PostgreSQL) | https://github.com/mingjing-zhang/week-04-api |
| Frontend (Next.js 16 + Tailwind) | https://github.com/mingjing-zhang/week-04-frontend |

Both repos are public. `.env` (backend) and `.env.local` (frontend) are excluded from version control via `.gitignore` — verified via the GitHub UI.

---

## 2. How to run the whole stack

Backend + database (in two containers via Docker Compose):
```bash
git clone https://github.com/mingjing-zhang/week-04-api.git
cd week-04-api
echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/booktracker" > .env
docker compose up --build
# Backend → http://localhost:8000  (Swagger at /docs)
```

Frontend (in another terminal):
```bash
git clone https://github.com/mingjing-zhang/week-04-frontend.git
cd week-04-frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm install
npm run dev
# Frontend → http://localhost:3000
```

---

## 3. Screenshots

All screenshots live in the backend repo under [`screenshots/`](https://github.com/mingjing-zhang/week-04-api/tree/main/screenshots).

### Persistence proof (lab submission item 3)
- [`01-persistence-get-books.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/01-persistence-get-books.png) — `GET /books` in Swagger UI returning 3 books after the FastAPI server was restarted. The data survives because PostgreSQL stores it in the `pgdata` Docker volume, not in the app process.

### Full CRUD flow (lab submission item 4)
| # | Screenshot | Step |
|---|---|---|
| 02 | [`02-flow-list-page.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/02-flow-list-page.png) | `/books` list with existing books |
| 03 | [`03-flow-add-form.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/03-flow-add-form.png) | `/books/new` form filled out |
| 04 | [`04-flow-list-with-new-book.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/04-flow-list-with-new-book.png) | List after submitting — new book appears |
| 05 | [`05-flow-detail-page.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/05-flow-detail-page.png) | `/books/{id}` detail page with action buttons |
| 06 | [`06-flow-after-update.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/06-flow-after-update.png) | Detail page after PUT — status pill updated |
| 07 | [`07-flow-deleting.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/07-flow-deleting.png) | Delete confirm dialog |
| 08 | [`08-flow-after-delete.png`](https://github.com/mingjing-zhang/week-04-api/blob/main/screenshots/08-flow-after-delete.png) | List after deletion — book is gone |

---

## 4. Reflection

Full reflection: [`reflection.md`](https://github.com/mingjing-zhang/week-04-api/blob/main/reflection.md)

Covers all six required questions plus closing observations on the Java EE → modern stack mental remapping, Python + AI synergy, and how AI coding assistants change what kind of experience is valuable.

---

## 5. Where to find each rubric item

A navigation index for the grader — every line from the lab's rubric mapped to the file or location that satisfies it. (Scoring is up to the grader; this is just a "where to look" map.)

| Rubric line | Where in the submission |
|---|---|
| Code split into `database.py`, `models.py`, `schemas.py`, `main.py` | Backend repo top-level Python files |
| PostgreSQL connected via Docker Compose | [`docker-compose.yml`](https://github.com/mingjing-zhang/week-04-api/blob/main/docker-compose.yml) |
| All CRUD endpoints working with real database | [`main.py`](https://github.com/mingjing-zhang/week-04-api/blob/main/main.py) — GET (list+detail+stats), POST, PUT, DELETE |
| Data persists across server restarts | Screenshot 01 |
| `.env` excluded from Git | [`.gitignore`](https://github.com/mingjing-zhang/week-04-api/blob/main/.gitignore) |
| CORS configured in backend | `main.py` — `CORSMiddleware` with `allow_origins=["http://localhost:3000"]` |
| Books list page fetches and displays from backend | [`app/books/page.tsx`](https://github.com/mingjing-zhang/week-04-frontend/blob/main/app/books/page.tsx) |
| Add book form POSTs and updates list | [`app/books/new/page.tsx`](https://github.com/mingjing-zhang/week-04-frontend/blob/main/app/books/new/page.tsx) |
| Detail page with update and delete works | [`app/books/[id]/page.tsx`](https://github.com/mingjing-zhang/week-04-frontend/blob/main/app/books/%5Bid%5D/page.tsx) |
| Loading and error states handled | All three pages — `loading`, `error` state, early returns |
| Environment variable used for API URL | `process.env.NEXT_PUBLIC_API_URL` referenced in every fetch |
| Reflection complete | `reflection.md` answers all 6 questions |

---

## 6. Notes for the grader

- **Backend architecture:** four-file split (database, models, schemas, main). FastAPI uses `Depends(get_db)` for per-request SQLAlchemy sessions. The table is auto-created at startup via `Base.metadata.create_all(...)`.
- **Frontend architecture:** Next.js 16 App Router. All three book pages are Client Components (`"use client"`) because they use `useEffect`/`useState`/`useRouter`. Root layout adds a sitewide nav (Home / My Books / Add Book).
- **CORS:** `CORSMiddleware` whitelists `http://localhost:3000` exactly. Verified by browser dev tools (no errors) and by curl-vs-browser parity.
- **Persistence:** Postgres data sits in the named volume `pgdata`. `docker compose down` keeps it; `docker compose down -v` would wipe it.
