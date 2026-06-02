# Number Lookup

A lightweight PoC web app: enter any number, look it up in a database, and optionally save a text note for it. Notes are immutable once saved. Page colors are derived from the number itself.

---

## Quick Start — Docker

**Prerequisites:** Docker Desktop installed and running.

```bash
# Clone the repo
git clone <your-repo-url>
cd WebApp

# Build and start (database persists in a Docker named volume)
docker compose up --build
```

Open [http://localhost:5000](http://localhost:5000).

To stop: `Ctrl+C`, then `docker compose down`.

> The SQLite database is stored in a Docker named volume (`db_data`) and survives container restarts. To wipe all saved data: `docker compose down -v`.

---

## Local Dev (no Docker)

**Prerequisites:** Python 3.12+

```bash
pip install -r requirements.txt
py app.py          # Windows
# python app.py    # macOS/Linux
```

Open [http://localhost:5000](http://localhost:5000).

The database file (`numbers.db`) is created automatically next to `app.py`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-change-in-production-abc123xyz` | Flask session signing key. **Change this before deploying.** |
| `DATABASE_PATH` | `numbers.db` (next to `app.py`) | Absolute path to the SQLite file. In Docker defaults to `/data/numbers.db`. |

Copy `.env.example` to `.env` and fill in values for local overrides.

---

## Architecture

```
Browser → Gunicorn (WSGI) → Flask → SQLite
```

- **Flask** handles routing and session management (session-backed `/view` — no number in the URL)
- **SQLite** stores number → text pairs (immutable after first save)
- **Gunicorn** (2 workers) serves requests in production; Flask dev server is used locally
- **Colors** are computed server-side from the number string (full 24-bit RGB, no external dependencies)

### Scaling Path

This PoC uses Flask + SQLite, suitable for development and demo use. For production at scale:

| Layer | PoC | Production |
|---|---|---|
| App server | Flask dev server | Gunicorn / Uvicorn + FastAPI |
| Database | SQLite | PostgreSQL + PgBouncer |
| Cache | None | Redis (immutable data — cache never invalidates) |
| Proxy | None | Nginx (TLS, load balancing) |

---

## Project Structure

```
app.py              # Flask routes, validation, session handling, security headers
db.py               # SQLite layer (thin interface, swappable for PostgreSQL)
colors.py           # Number → background color + contrast text color
templates/
  base.html         # Shared layout
  index.html        # Home / search page
  number.html       # Number detail / save page (dynamic color scheme)
static/
  style.css         # Base styles
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```
