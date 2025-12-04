**HMS1 — Codebase Improvements & Recommendations**

This document collects prioritized, actionable improvements for the Hotel Management System repository. Recommendations are grouped by priority and by area (backend, database, security, tests/CI, frontend, developer ergonomics). Each item includes why it matters and one or more concrete next steps (code snippets or commands when appropriate).

---

**High Priority (should be addressed first)**

- Security: implement proper authentication tokens (JWT) and refresh flows.
  - Why: current `backend/app/api/auth.py` accepts login/register but returns only a success detail; there's no token or session management. This is critical for protected endpoints and auditability.
  - Action: add a `backend/app/core/security.py` implementation that builds/validates JWTs with expiration and refresh tokens. Use `python-jose` (already in requirements) and store secrets in environment variables. Replace the current `auth.login` response with an access token and expiry.
  - Example (concept):

    ```py
    from datetime import datetime, timedelta
    from jose import jwt

    SECRET = os.getenv("JWT_SECRET")
    ALGO = "HS256"

    def create_access_token(sub: str, expires_minutes: int = 60):
        to_encode = {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)}
        return jwt.encode(to_encode, SECRET, algorithm=ALGO)
    ```

- Password hashing policy: centralize and standardize.
  - Why: `auth.py` currently uses raw `bcrypt` with a pre-hash for >72 bytes. Prefer a standard library (e.g. `passlib`'s `CryptContext`) so algorithms and parameters are managed centrally and upgraded easily.
  - Action: consolidate hashing into `core/security.py` or `services/user_service.py`, and migrate stored hashes consistently. If you want to keep the 72-byte pre-hash, document and centralize it.

- Fix dependency mismatch (async vs sync SQLAlchemy drivers).
  - Why: `pyproject.toml` and `requirements.txt` include async drivers (`asyncpg`, `sqlalchemy[async]`) while the app uses a sync engine in `backend/app/db/session.py`. Keep dependencies congruent: either migrate the codebase fully to async/await patterns, or clean async-only packages from dependencies and use sync drivers (psycopg2) only.
  - Action: decide sync vs async. If staying sync, remove `asyncpg` and `sqlalchemy[async]` from `pyproject.toml` and `requirements.txt`. If migrating to async, convert services and APIs to use `async def`, `AsyncSession`, and `asyncpg`-backed engine.

---

**Medium Priority (important for robustness & maintainability)**

- Add structured logging and centralized error handling.
  - Why: `main.py` has no exception handlers or logging setup. Add a logging config using Python `logging` and create FastAPI exception handlers for HTTP/validation/database errors.
  - Action: create `backend/app/core/logging.py` and register exception handlers in `main.py`.

- Harden CORS & security headers.
  - Why: `main.py` currently sets `allow_origins=["*"]`. For production, restrict origins and set secure headers (Content-Security-Policy, X-Frame-Options, etc.). Use `Starlette` middleware or server-level config.

- DB session configuration and engine options.
  - Why: `engine = create_engine(sync_db_url, echo=True, future=True)` sets `echo=True` (noisy in prod). Consider connection pool tuning, `pool_size`, `max_overflow`, and `pool_pre_ping=True` for production.

- Add database constraints and indexes where missing.
  - Why: `models.py` defines many indexes but verify fields used in WHERE/JOIN clauses have indexes (e.g., booking range queries). Consider partial indexes for active bookings and FK constraints with ON DELETE policies.

- Improve service-layer transactions and error handling.
  - Why: `RoomService.create_room` directly commits. Wrap operations in transactions and handle integrity errors to return meaningful API errors (e.g., unique constraint violations).

- Pagination, filtering, sorting on list endpoints.
  - Why: `list_rooms()` currently returns all rows. For production, add pagination parameters, limit/offset or cursor-based pagination, and filters (room_type, price range, availability).

---

**Low Priority / Nice-to-have**

- Observability: metrics (Prometheus), traces (OpenTelemetry).
- Rate limiting for public endpoints and brute-force protection for auth.
- Background tasks for long-running operations (email notifications, payment processing).
- Use `mypy`/type hints and CI step to run static type checks.

---

**Frontend Recommendations**

- Accessibility & semantics
  - Add ARIA attributes, proper labels, and keyboard focus management (especially for the modal). Make the theme toggle reachable via keyboard and add `aria-pressed` state.

- Responsive & mobile-first styles
  - Ensure the two-panel layout collapses cleanly on small screens. Test with common viewport widths and add breakpoints.

- UX improvements
  - Add explicit loading states, disable buttons while requests are in flight, and provide inline validation errors on the forms.

- Security
  - Sanitize any HTML inserted via `innerHTML` (avoid if possible). Prefer `textContent` and template rendering for values. Consider a CSP header.

- Theming
  - Use `prefers-color-scheme` CSS media query as the initial default, falling back to your stored preference.

---

**Tests & CI**

- Increase unit test coverage and test important layers: services, utils, and edge cases.
  - Add tests for concurrency-related booking conflicts and availability checks.

- Add integration tests that exercise the full stack: create room type → create room → create guest → create booking.

- Extend CI pipeline to run:
  - ruff/flake8 linting
  - ruff or black formatting check
  - mypy static type checks (optional)
  - pytest with coverage

Example GitHub Actions steps (concept):

```yaml
steps:
  - uses: actions/checkout@v4
  - name: Set up Python
    uses: actions/setup-python@v4
    with: python-version: '3.12'
  - name: Install deps
    run: python -m pip install -r requirements.txt
  - name: Lint
    run: ruff check .
  - name: Test
    run: pytest -q
```

---

**Docker / Deployment**

- Provide a production-ready `Dockerfile` and `docker-compose.override.yml` that:
  - Run migrations (Alembic) during container startup
  - Use Uvicorn with Gunicorn (or just Uvicorn workers) and proper workers, timeouts, and logging
  - Supply environment variables via secrets or `.env` file

- Example run command for production (compose):

```pwsh
docker compose up --build -d
```

---

**Repository Hygiene & Developer Experience**

- Remove unused/incorrect dependencies from `pyproject.toml` and keep it in sync with `requirements.txt`.
- Add `CONTRIBUTING.md` and `.env.example` documenting required env vars (DATABASE_URL, JWT_SECRET, etc.).
- Add pre-commit hooks for `ruff`, `black`, and `isort`.

---

**File-specific notes (actionable)**

- `backend/app/core/security.py` — currently empty: implement JWT helpers, password hashing wrapper, and token dependency for FastAPI `Depends`.

- `backend/app/api/auth.py` — return access tokens instead of plaintext success; centralize hashing; avoid mutating Pydantic input objects in-place.

- `backend/app/db/session.py` — set `echo=False` in prod; consider `pool_pre_ping=True`; document `DATABASE_URL` format and behavior; add connection health checks in deploy.

- `backend/app/services/*.py` — add typed return annotations, exception handling, and transaction boundaries. Unit test each service.

- `backend/app/main.py` — restrict `CORS` in production; add middleware for logging, error handling, and security headers.

- `frontend/js/app.js` — avoid `innerHTML` for untrusted content; add ARIA attributes and loading indicators; use `fetch` error handling to parse JSON safely.

---

**Quick Starter Tasks (do these this week)**

1. Implement `backend/app/core/security.py` with JWT create/verify, move hashing to here.
2. Update `auth.login` to return access token + expiry; protect route examples using a `get_current_user` dependency.
3. Add unit tests for `UserService` and `RoomService` and CI step to run tests.
4. Create `.env.example` listing `DATABASE_URL`, `JWT_SECRET`, `DATABASE_URL` sample.
5. Clean `pyproject.toml` to reflect chosen sync-or-async strategy and pin minimal necessary libs.

---

If you'd like, I can: run an automated scan to suggest exact code diffs for any one of the high-priority items (for example: implement JWT auth in `core/security.py`, and update `auth.py` to return tokens). Tell me which item you'd like me to implement first and I'll create the changes and tests for it.
