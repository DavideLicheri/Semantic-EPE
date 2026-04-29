# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ECES (EURING Code Evolution System) is a web application for managing, visualizing, and converting EURING bird ringing codes across four historical versions (1966, 1979, 2000, 2020). It is an internal ISPRA tool, all UI text is hardcoded in Italian (an i18n system was removed due to race condition bugs). The system uses JWT authentication with three roles: `user`, `matrix_editor`, `super_admin`.

## Commands

### Backend

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. python3 main.py          # Starts on http://localhost:8000; /docs for Swagger UI
```

Run all tests (from repo root):
```bash
cd backend && python -m pytest
```

Run a single test file:
```bash
cd backend && python -m pytest tests/test_version_loading.py -v
```

Run tests with a specific marker (unit, integration, property, slow):
```bash
cd backend && python -m pytest -m unit
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Dev server on http://localhost:3000
npm run build    # tsc + vite build → dist/
npm run lint     # ESLint (0 warnings tolerance)
npm run preview  # Preview production build
```

### Docker (PostgreSQL only for local analytics)

```bash
docker-compose up postgres   # Just the database
docker-compose up            # Full stack including backend container
```

## Architecture

### Data Flow

```
React SPA (port 3000) ──fetch/axios──► FastAPI (port 8000)
                                            │
                          ┌─────────────────┼─────────────────┐
                          ▼                 ▼                  ▼
                     JSON files       PostgreSQL           users.json
                  (EURING versions   (analytics &          (auth only)
                   + mappings)        query logs)
```

The Vite config sets `base: '/eces/'`, so in production the frontend is served under the `/eces/` path prefix via Nginx.

### Backend Layer Structure

`main.py` → three API routers → services → repositories → data files

- **`app/api/`** — Three routers: `euring_api.py` (EURING operations), `auth_api.py` (JWT auth), `analytics_api.py` (super_admin only)
- **`app/services/`** — All business logic. Key services:
  - `skos_manager.py` — Loads and caches EURING version definitions from JSON; the central service for version data
  - `recognition_engine.py` — Identifies EURING version of a string using length + discriminant pattern analysis (>95% accuracy, no ML)
  - `conversion_service.py` + `semantic_converter.py` — Convert strings between versions via semantic field mapping
  - `lookup_table_service.py` — Provides valid-value tables for coded fields (sex, age, etc.)
  - `domain_evolution_analyzer.py` / `domain_compatibility_assessor.py` / `semantic_field_grouper.py` — Domain panel analysis
  - `usage_logger.py` / `database_service.py` — Log queries to PostgreSQL for analytics
- **`app/repositories/skos_repository.py`** — Reads/writes EURING JSON files; supports cache invalidation on field edits
- **`app/auth/`** — JWT with bcrypt. `auth_service.py` handles hashing; `dependencies.py` exposes FastAPI `Depends` guards (`get_current_active_user`, `require_matrix_edit_permission`, `require_super_admin`, `get_current_user_optional`)
- **`app/models/euring_models.py`** — All Pydantic models: `EuringVersion`, `FieldDefinition`, `ConversionMapping`, `FieldMapping`, `SemanticDomain` enum, etc.

### Data Files (`backend/data/`)

- `euring_versions/versions/euring_{1966,1979,2000,2020}.json` — Full field definitions per version (positions, lengths, types, lookup values, semantic domain assignments)
- `euring_versions/conversion_mappings.json` — Field-to-field mapping rules across version pairs
- `euring_versions/domain_evolutions/` — Per-domain evolution data for the DomainPanel
- `auth/users.json` — User records with bcrypt-hashed passwords; the `super_admin` default is `admin`/`admin`

### Frontend Structure

Single-page app with tab navigation. Auth state lives in `App.tsx` (no Redux). JWT stored in `localStorage` under key `eces_token`.

- **`services/auth.ts`** — `AuthService` singleton handles login, logout, token storage, expiry check
- **`services/api.ts`** — Typed API client for all EURING endpoints
- **`types/euring-types.ts`** — TypeScript types matching backend Pydantic models
- Major components: `RecognitionPanel`, `ConversionPanel`, `StringNavigator` (batch, paginated 50/page), `EuringMatrix` (tabular cross-version view), `PositionalMatrixEditor` (field editing with side panel), `DomainPanel` (domain evolution/charts/compatibility)
- Each component has a co-located `.css` file; styling uses plain CSS modules, no CSS-in-JS

## Key Conventions

### Authentication & Permissions

- New users register with `is_active: false`; a `super_admin` must approve them
- Endpoint guards via FastAPI `Depends`: import from `app.auth.dependencies` and use `get_current_active_user`, `require_matrix_edit_permission`, or `require_super_admin`
- Frontend checks token expiry via `authService.isTokenExpired()` on every page load; expired tokens trigger auto-logout

### EURING Data Editing

- Field edits go through `SKOSRepository.save_version()` which writes back to the JSON files in `data/euring_versions/versions/`
- After a save, `SKOSManagerImpl._version_model` and `_version_cache` must be invalidated (set to `None`/clear) so the next request reloads from disk

### Backend Environment Variables

All use the `ECES_` prefix:

| Variable | Default | Purpose |
|---|---|---|
| `ECES_SECRET_KEY` | `eces-ispra-secret-key-2024` | JWT signing key |
| `ECES_ENVIRONMENT` | `development` | Enables uvicorn reload when `development` |
| `ECES_CORS_ORIGINS` | `http://localhost:3000,...` | Comma-separated allowed origins |
| `ECES_HOST` / `ECES_PORT` | `0.0.0.0` / `8000` | Bind address |
| `DATABASE_URL` | — | PostgreSQL for analytics; analytics is skipped gracefully if unavailable |

### Known Active Bug

Batch parsing fails with a Pydantic validation error when 3+ identical EURING strings are submitted (`EuringBatchParseResponse` is missing `euring_string` for duplicate entries). Workaround: use distinct strings or parse individually. Fix target: `backend/app/models/euring_models.py` (`EuringBatchParseResponse`) and the batch handler in `euring_api.py`.

## Testing

Tests use `pytest` + `pytest-asyncio` + `hypothesis`. The test suite is sparse — `tests/test_version_loading.py` covers `VersionLoaderService` and `SKOSManagerImpl` integration. Tests must be run from the `backend/` directory (or with `PYTHONPATH` set to include `backend/`) because imports are relative to that root.
