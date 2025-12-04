# Changelog

All notable changes to this project are documented in this file.

## [Unreleased] - 2025-12-04

- Pydantic compatibility
  - Replaced call-expression field types (`constr`, `conint`) in schema annotations with plain `str`/`int` types and `pydantic.Field(...)` constraints to avoid type-checker errors (Pylance/pyright) and maintain runtime validation.
  - Migrated class-based `Config` uses (`orm_mode = True`) to Pydantic v2 configuration via `model_config = ConfigDict(from_attributes=True)`.
- Imports
  - Converted package imports under `backend/app` to relative imports so the application loads consistently whether run using `uvicorn backend.app.main:app` or from the package root.
- Database
  - Simplified DB settings loading to use `python-dotenv` + `os.getenv`.
  - Switched to a synchronous SQLAlchemy engine with a `get_db()` dependency generator to avoid requiring platform-specific builds for async DB drivers on Windows.
- Utilities
  - Implemented `backend/app/utils/availability.py::is_room_available` to check overlapping bookings and support `exclude_booking_id` for safe updates.
- Tests & CI
  - Added `tests/test_availability.py` and `tests/test_api_smoke.py` to validate availability logic and a root API endpoint.
  - Added `tests/conftest.py` with fixtures and a TestClient `client` fixture that overrides DB dependency for isolated testing.
  - Added GitHub Actions workflow at `.github/workflows/ci.yml` to run tests on push/PR.
- Linting & tooling
  - Added `ruff` to dev tooling and fixed lint issues across tests/code.

Notes
- The codebase now targets Pydantic v2 patterns. There are some remaining benign deprecation warnings originating from third-party packages.
- If you prefer an async DB stack, we can revert the DB changes and add `asyncpg`; note that installing `asyncpg` on Windows may require Microsoft C++ Build Tools.

