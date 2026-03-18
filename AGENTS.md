# AGENTS.md

Team-shared operating rules for AI coding agents in `ph-travel-app`.

## Metadata

- Owner: Engineering Team (assumption: no explicit CODEOWNERS/policy owner file found)
- Last reviewed: 2026-03-18
- Review cadence: Monthly and on workflow/tooling changes (assumption)

## Project context

- Monorepo with frontend (`frontend/atla`) and backend (`backend`) plus docs/workflows (`docs/`, `.github/`) (from `README.md`, `docs/CONTRIBUTING.md`).
- Frontend stack: React 19 + TypeScript + Vite + TanStack Router + Tailwind CSS (from `README.md`, `frontend/atla/package.json`).
- Backend stack: FastAPI + Python 3.11+ + SQLModel + Alembic + PostgreSQL/Supabase + LangChain/Gemini (from `README.md`, `ARCH.md`, `backend/requirements.txt`).
- CI present in repo: frontend PR workflow only, triggered for frontend/workflow changes on `main` and `develop` PRs (from `.github/workflows/frontend-ci.yml`).
- Supported development OS appears cross-platform (Windows and macOS/Linux setup instructions exist) (from `README.md`, `SETUP.md`, `docs/CONTRIBUTING.md`).

## Commands (Use Exactly)

- Install
  - Frontend dependencies: `cd frontend/atla && npm ci` (from `.github/workflows/frontend-ci.yml`).
  - Frontend Node version: `cd frontend/atla && nvm use 20` (from `frontend/atla/.nvmrc`, `.github/workflows/frontend-ci.yml`).
  - Backend env + deps (both OS): `cd backend && python -m venv venv && pip install -r requirements.txt` (from `README.md`, `SETUP.md`, `docs/CONTRIBUTING.md`).
  - Backend venv activate (Windows): `cd backend && venv\Scripts\activate` (from `README.md`, `SETUP.md`).
  - Backend venv activate (macOS/Linux): `cd backend && source venv/bin/activate` (from `README.md`, `SETUP.md`).

- Lint
  - Frontend: `cd frontend/atla && npm run lint` (from `frontend/atla/package.json`, `README.md`).
  - Backend: `cd backend && ruff check app` (from `README.md`, `backend/pyproject.toml`).

- Typecheck
  - Frontend: `cd frontend/atla && npm run generate:routes && npm run typecheck` (from `.github/workflows/frontend-ci.yml`, `frontend/atla/package.json`).
  - Backend: no documented dedicated static typecheck command (gap confirmed from `backend/pyproject.toml`, `README.md`, `docs/CONTRIBUTING.md`).

- Test
  - Backend: `cd backend && pytest` (from `README.md`, `SETUP.md`, `docs/PULL_REQUESTS.md`).
  - Frontend: no `test` script defined; do not claim automated frontend tests unless added in the same change (from `frontend/atla/package.json`).

- Verify (before PR or done claim)
  - Frontend: `cd frontend/atla && npm run generate:routes && npm run typecheck && npm run build && npm run lint` (from `.github/workflows/frontend-ci.yml`, `docs/CONTRIBUTING.md`).
  - Backend: `cd backend && ruff check app && pytest` (assumption based on `README.md` + `docs/PULL_REQUESTS.md`; no single canonical `verify` command documented).

## Policy tiers

- `MUST`: blocking requirement; do not mark task complete if unmet.
- `SHOULD`: strong default; deviation requires explicit rationale in completion report.
- `MAY`: optional guidance; apply when useful and low-risk.

## Rule precedence

1. Safety and data integrity
2. Security
3. User intent
4. Workflow/process rules
5. Style preferences

## Agent behavior

- `MUST` state exact impact and wait for confirmation before destructive actions (delete/overwrite unrelated content, force push, reset, dropping schema/tables).
- `MUST` create a short, checkable plan before non-trivial work (3+ steps, cross-file edits, architecture-impacting changes).
- `MUST` stop and re-plan if new evidence invalidates the plan.
- `MUST` stop after 2 failed attempts and return exactly:

```text
Blocked Report
1) What I tried:
2) Evidence (error/log/output):
3) Current hypothesis:
4) Exact blocker:
5) Recommended next step:
```

- `MUST` follow ambiguity protocol: ask exactly one focused question when missing critical context blocks correctness; if unanswered, apply the safest explicit default and record it under assumptions in the report.

## Subagent invocation policy

- `SHOULD` execute directly for normal implementation.
- `MUST` use specialist routing when scope matches:
  - `@debugger` for failing tests/checks with unclear root cause.
  - `@tester` for validating new/changed behavior before handoff.
  - `@gh-operator` for GitHub issue/PR operations.
  - `@pr-reviewer` for complex/high-risk PR review.
- `MUST` use explicit `@subagent` routing if auto-routing fails once.

## Risk-based routing matrix

| Scenario | Risk level | Route |
|---|---|---|
| Failing tests, unclear cause | High | `@debugger` |
| Behavior change before handoff | Medium | `@tester` |
| Create/update issue or PR metadata | Medium | `@gh-operator` |
| Security/auth/data-model/CI workflow changes | High | `@pr-reviewer` + human review (assumption for extra safeguard) |
| Small docs or scoped refactor with clear checks | Low | Direct execution |

## Execution quality

- `MUST` make the smallest correct change and avoid unrelated refactors.
- `MUST` fix root cause, not symptoms, unless user requests a temporary workaround.
- `SHOULD` prefer explicit, readable code and guard clauses over deep nesting.
- `MUST` handle errors intentionally; no silent failure paths.
- `MUST` remove dead code instead of commenting it out.

## Definition of done contract

- `MUST` include a completion report with all of:
  - commands run
  - key results
  - what is verified vs not verified
  - residual risks/limitations
- `MUST` avoid claiming "done" or "fixed" without command evidence.

## Verification before done

- `MUST` run relevant verify commands for touched areas (frontend/backend) and report outcomes.
- `MUST` compare expected before/after behavior for behavior changes.
- `MUST` verify UI changes on desktop and mobile (manual verification allowed; include what was checked).
- `SHOULD` call out skipped checks with reason (for example, missing env/secrets or unavailable service).

## Security non-negotiables

- `MUST` never commit secrets/credential files (`.env*`, `*.pem`, `*.key`, `credentials*.json`).
- `MUST` scan staged changes for secrets/tokens before commit.
- `MUST` treat these keys as high sensitivity: `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, `GOOGLE_API_KEY`, `BRAVE_API_KEY`, `REDIS_URL`, `SECRET_KEY` (from `SETUP.md`, `backend/.env.example`).
- `MUST` avoid `eval()`/unsafe dynamic execution with unsanitized input.
- `MUST` use parameterized ORM/query patterns; never concatenate raw user input into SQL.

## Git and PR standards

- `MUST` follow GitHub Flow: branch from `main`; never commit directly to `main` (from `docs/BRANCHING.md`, `docs/CONTRIBUTING.md`).
- `MUST` use branch prefixes: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`, `hotfix/` (from `docs/BRANCHING.md`).
- `MUST` use Conventional Commits `type(scope): description`; keep subject under 72 chars (from `docs/COMMITS.md`).
- `MUST` include issue linkage in PR body (for example `Closes #123`) (from `.github/PULL_REQUEST_TEMPLATE.md`, `docs/PULL_REQUESTS.md`).
- `MUST` not force-push to `main` or rewrite shared history (from `docs/PULL_REQUESTS.md`).

## Scope-control rules

- `MUST` keep bugfix PRs free of unrelated refactors.
- `MUST` keep one concern per PR (feature/fix/docs/chore) (from `docs/BRANCHING.md`, `docs/PULL_REQUESTS.md`).
- `MUST` propose splitting when a PR touches more than 3 unrelated concerns (baseline safeguard adopted in this file).

## Critical paths and extra review triggers

- Sensitive paths requiring extra care:
  - Auth/session: `backend/app/api/auth.py`, `backend/app/api/deps.py`, `backend/app/db/supabase.py`, `frontend/atla/src/routes/login.tsx`, `frontend/atla/src/routes/signup.tsx` (from project structure and auth context in `README.md`, `ARCH.md`).
  - Secrets/config: `backend/app/config.py`, `backend/.env.example`, `frontend/atla/.env.example` (from `SETUP.md`, repo structure).
  - Data model/schema: `backend/app/models/*.py`, `backend/alembic/versions/*.py` (from `ARCH.md`).
  - AI behavior/tooling: `backend/app/ai/**`, `backend/app/services/chat_service.py` (from `ARCH.md`).
  - CI policy: `.github/workflows/*.yml` (from repo workflows).
- Extra review trigger: `SHOULD` request at least one human review when any sensitive path above changes (assumption-based safeguard; standard review is optional per docs).

## Team review policy

- Required reviewers for standard PRs: none (from `docs/PULL_REQUESTS.md`).
- CI expectation for merge: frontend Type Check and Build jobs must pass when the frontend workflow is triggered (from `.github/workflows/frontend-ci.yml`).
- Lint expectation: frontend lint is disabled in CI; run `npm run lint` locally and report status in PR/testing notes (from `.github/workflows/frontend-ci.yml`).
- PR scope expectation: one concern per PR; fill testing and issue-link sections in PR template (from `docs/BRANCHING.md`, `.github/PULL_REQUEST_TEMPLATE.md`).

## Delta from global baseline

- Baseline sections included directly in this file: Rule precedence, Agent behavior, Subagent invocation policy, Execution quality, Verification before done, Security non-negotiables, Git and PR standards.
- Intentional deviations:
  - Added explicit `MUST`/`SHOULD`/`MAY` tiers for enforceability in this monorepo.
  - Added command matrix with evidence notes so agents can run checks consistently.
  - Added assumption-based extra review trigger for sensitive paths while preserving documented optional-review policy.

## Validation notes (assumptions, unresolved gaps)

- Assumption: backend local verify gate is `ruff check app && pytest`; no canonical single backend `verify` command exists in docs.
- Gap: `docs/PULL_REQUESTS.md` describes backend CI checks, but only `.github/workflows/frontend-ci.yml` is present.
- Assumption: explicit risk-based routing and >3-concern split rule are team safeguards adopted here (not directly documented elsewhere).
- Self-check: all required baseline sections present; commands/policies are evidence-backed or marked assumptions; no personal local paths included.
