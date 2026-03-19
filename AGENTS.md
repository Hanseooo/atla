# AGENTS.md

Team-shared operating rules for AI coding agents in `ph-travel-app`.

## Metadata

- Owner: Hans
- Last reviewed: 2026-03-19
- Review cadence: Monthly and on workflow/tooling changes

## Project context

- Monorepo with frontend (`frontend/atla`) and backend (`backend`) plus docs/workflows (`docs/`, `.github/`) (from `README.md`, `docs/CONTRIBUTING.md`).
- Frontend stack: React 19 + TypeScript + Vite + TanStack Router + Tailwind CSS (from `README.md`, `frontend/atla/package.json`).
- Backend stack: FastAPI + Python 3.11+ + SQLModel + Alembic + PostgreSQL/Supabase + LangChain + Gemini integrations (from `README.md`, `ARCH.md`, `backend/requirements.txt`).
- CI in repo: frontend PR workflow only, scoped to frontend/workflow changes on PRs targeting `main` and `develop` (from `.github/workflows/frontend-ci.yml`).
- Development appears cross-platform (Windows and macOS/Linux instructions exist) (from `README.md`, `SETUP.md`, `docs/CONTRIBUTING.md`).

## Commands (Use Exactly)

- Install
  - Frontend Node version: `cd frontend/atla && nvm use 20` (from `frontend/atla/.nvmrc`, `.github/workflows/frontend-ci.yml`).
  - Frontend dependencies (CI-reproducible): `cd frontend/atla && npm ci` (from `.github/workflows/frontend-ci.yml`).
  - Backend env + deps: `cd backend && python -m venv venv && pip install -r requirements.txt` (from `README.md`, `SETUP.md`, `docs/CONTRIBUTING.md`).
  - Backend venv activate (Windows): `cd backend && venv\Scripts\activate` (from `README.md`, `SETUP.md`).
  - Backend venv activate (macOS/Linux): `cd backend && source venv/bin/activate` (from `README.md`, `SETUP.md`).

- Lint
  - Frontend: `cd frontend/atla && npm run lint` (from `frontend/atla/package.json`, `README.md`).
  - Backend: `cd backend && ruff check app` (from `README.md`, `backend/pyproject.toml`).

- Typecheck
  - Frontend: `cd frontend/atla && npm run generate:routes && npm run typecheck` (from `.github/workflows/frontend-ci.yml`, `frontend/atla/package.json`).
  - Backend: no documented dedicated static typecheck command (gap confirmed from `backend/pyproject.toml`, `README.md`, `docs/CONTRIBUTING.md`).

- Test
  - Frontend: `cd frontend/atla && npm run test` (from `frontend/atla/package.json`).
  - Backend: `cd backend && pytest` (from `README.md`, `SETUP.md`, `docs/PULL_REQUESTS.md`).

- Verify (before PR or done claim)
  - Frontend: `cd frontend/atla && npm run generate:routes && npm run typecheck && npm run build && npm run lint` (from `.github/workflows/frontend-ci.yml` plus local lint note in same workflow and `docs/CONTRIBUTING.md`).
  - Backend: `cd backend && ruff check app && pytest` (assumption based on documented backend lint + test commands; no single canonical verify command documented).

## Policy tiers (`MUST` / `SHOULD` / `MAY`)

- `MUST`: blocking requirement; do not mark work complete if unmet.
- `SHOULD`: strong default; deviations require explicit rationale in completion report.
- `MAY`: optional guidance when useful and low-risk.

## Rule precedence

1. Safety and data integrity
2. Security
3. User intent
4. Workflow/process rules
5. Style preferences

## Agent behavior

- `MUST` state exact impact and wait for confirmation before destructive actions (delete/overwrite unrelated content, force push, reset, dropping schema/tables).
- `MUST` create a short, checkable plan before non-trivial work (3+ steps, cross-file edits, architecture-impacting changes).
- `MUST` stop and re-plan if new evidence invalidates the current plan.
- `MUST` use ambiguity protocol: ask exactly one focused question when critical context is missing; if unanswered, apply the safest explicit default and record it under assumptions.
- `MUST` stop after 2 failed attempts and return exactly:

```text
Blocked Report
1) What I tried:
2) Evidence (error/log/output):
3) Current hypothesis:
4) Exact blocker:
5) Recommended next step:
```

## Subagent invocation policy

- `SHOULD` execute directly for normal implementation and small scoped tasks.
- `MUST` route to a specialist capability when the task matches the capability model below.
- `MUST` use explicit `@subagent` routing syntax if auto-routing fails once.
- `MUST` not block delivery if alias tooling is unavailable; use command-driven fallback.

## Capability model and optional aliases

- Canonical capabilities:
  - `GitHub Ops` (optional alias: `@gh-operator`)
  - `Product Discovery` (optional alias: `@product-reviewer`)
  - `Architecture Decision` (optional alias: `@architect`)
  - `Phased Planning` (optional alias: `@planner`)
  - `Research` (optional alias: `@researcher`)
  - `Test Validation` (optional alias: `@tester`)
  - `Test Repair` (optional alias: `@debugger`)
  - `Security Review` (optional alias: `@security-auditor`)
  - `Peer PR Review` (optional alias: `@pr-reviewer`)

## Capability routing matrix

| Scenario | Risk | Route |
|---|---|---|
| Failing tests/checks with unclear root cause | High | `Test Repair` (optional `@debugger`) |
| Behavior changes before handoff | Medium | `Test Validation` (optional `@tester`) |
| Create/update PRs, issues, labels, metadata | Medium | `GitHub Ops` (optional `@gh-operator`) |
| Ambiguous feature request or unclear UX intent | Medium | `Product Discovery` (optional `@product-reviewer`) |
| Multi-step implementation with dependencies | Medium | `Phased Planning` (optional `@planner`) |
| Security/auth/data-model/CI workflow changes | High | `Security Review` + `Peer PR Revie  w` (optional `@security-auditor`, `@pr-reviewer`) |
| Tradeoff-heavy architectural choices | High | `Architecture Decision` (optional `@architect`) |
| Version-sensitive external docs/tool behavior | Medium | `Research` (optional `@researcher`) |

## Capability fallbacks

- If `GitHub Ops` alias/tooling is unavailable: use `gh` CLI directly for issue/PR/check/workflow operations.
- If `Test Repair` or `Test Validation` alias/tooling is unavailable: run the documented lint/typecheck/test/verify commands, capture failures, fix, and re-run.
- If `Product Discovery`, `Architecture Decision`, `Phased Planning`, or `Research` alias/tooling is unavailable: produce an explicit written plan/tradeoff analysis with repo evidence and assumptions before coding.
- If `Security Review`/`Peer PR Review` alias/tooling is unavailable: run a manual changed-files security and risk review, then record findings in the completion report.

## Execution quality

- `MUST` make the smallest correct change with minimal blast radius.
- `MUST` fix root causes, not symptoms, unless a temporary workaround is explicitly requested.
- `MUST` avoid unrelated refactors while delivering scoped fixes/features.
- `SHOULD` prefer explicit, readable code and guard clauses over deep nesting.
- `MUST` handle errors intentionally; no silent failure paths.
- `MUST` remove dead code instead of commenting it out.

## Definition of done contract

- `MUST` include a completion report with all of: commands run, key results, verified vs not verified, and residual risks/limitations.
- `MUST` include expected before/after behavior when behavior changes were made.
- `MUST` not claim "done" or "fixed" without command evidence.

## Verification before done

- `MUST` run relevant verify commands for touched areas and report outcomes.
- `MUST` verify UI changes on desktop and mobile (manual verification allowed; include what was checked).
- `SHOULD` run frontend tests (`npm run test`) when frontend behavior changes are introduced (from `frontend/atla/package.json`).
- `SHOULD` call out skipped checks with a concrete reason (for example missing secrets/services).

## Security non-negotiables

- `MUST` never commit secrets/credential files (`.env*`, `*.pem`, `*.key`, `credentials*.json`).
- `MUST` scan staged changes for secrets/tokens before commit.
- `MUST` treat these keys as high sensitivity: `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, `GOOGLE_API_KEY`, `BRAVE_API_KEY`, `REDIS_URL`, `SECRET_KEY` (from `SETUP.md`, `backend/.env.example`).
- `MUST` avoid unsafe dynamic execution with unsanitized input (`eval`, equivalent patterns).
- `MUST` use parameterized ORM/query patterns; never concatenate raw user input into SQL.

## Git and PR standards

- `MUST` follow GitHub Flow: branch from `main`; never commit directly to `main` (from `docs/BRANCHING.md`, `docs/CONTRIBUTING.md`).
- `MUST` use branch prefixes: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`, `hotfix/` (from `docs/BRANCHING.md`).
- `MUST` use Conventional Commits `type(scope): description` and keep subject under 72 chars (from `docs/COMMITS.md`).
- `MUST` include issue linkage in PR body (for example `Closes #123`) (from `.github/PULL_REQUEST_TEMPLATE.md`, `docs/PULL_REQUESTS.md`).
- `MUST` not force-push to `main` or rewrite shared history (from `docs/PULL_REQUESTS.md`).

## Scope-control rules

- `MUST` keep bugfix PRs free of unrelated refactors.
- `MUST` keep one concern per PR (feature/fix/docs/chore) (from `docs/BRANCHING.md`, `docs/PULL_REQUESTS.md`).
- `MUST` propose split PRs when changes touch more than 3 unrelated concerns (assumption-based safeguard).

## Critical paths and extra review triggers

- Sensitive paths requiring extra care:
  - Auth/session: `backend/app/api/auth.py`, `backend/app/api/deps.py`, `backend/app/db/supabase.py`, `frontend/atla/src/routes/login.tsx`, `frontend/atla/src/routes/signup.tsx` (from repo structure + auth context in `README.md`, `ARCH.md`).
  - Secrets/config: `backend/app/config.py`, `backend/.env.example`, `frontend/atla/.env.example` (from `SETUP.md`, repo structure).
  - Data model/schema: `backend/app/models/*.py`, `backend/alembic/versions/*.py` (from `ARCH.md`).
  - AI behavior/tooling: `backend/app/ai/**`, `backend/app/services/chat_service.py` (from `ARCH.md`, repo structure).
  - CI policy/workflows: `.github/workflows/*.yml` (from repo structure).
- Extra review trigger: `SHOULD` request at least one human review when any sensitive path above changes (assumption-based safeguard; standard reviewers are optional per docs).

## Team review policy

- Required reviewers for standard PRs: none (from `docs/PULL_REQUESTS.md`).
- CI expectation for merge: frontend `Type Check` and `Build` jobs must pass when `frontend-ci.yml` is triggered (from `.github/workflows/frontend-ci.yml`).
- CI trigger scope: PRs to `main` or `develop` with changes under `frontend/atla/**` or `.github/workflows/frontend-ci.yml` (from `.github/workflows/frontend-ci.yml`).
- Lint expectation: frontend lint is disabled in CI; run `npm run lint` locally and report status in testing notes (from `.github/workflows/frontend-ci.yml`).
- PR scope expectation: keep one concern per PR and complete issue-link/testing sections in the PR template (from `docs/BRANCHING.md`, `.github/PULL_REQUEST_TEMPLATE.md`).

## Delta from global baseline

- Baseline sections included directly in this file: Rule precedence, Agent behavior, Subagent invocation policy, Execution quality, Verification before done, Security non-negotiables, Git and PR standards.
- Intentional deviations:
  - Added explicit `MUST`/`SHOULD`/`MAY` tiers for enforceability in this monorepo.
  - Added a command matrix with evidence notes to keep execution checkable.
  - Added capability-first model, routing matrix, and fallback rules to avoid tool-alias lock-in.
  - Added assumption-based split threshold (>3 unrelated concerns) and extra review trigger for sensitive paths.

## Validation notes (assumptions, unresolved gaps)

- Assumption: backend local verify gate is `ruff check app && pytest`; no canonical single backend verify command is documented.
- Gap: `docs/PULL_REQUESTS.md` mentions backend CI checks, but only `.github/workflows/frontend-ci.yml` exists in the repository.
- Gap: backend dedicated static typecheck command is not documented.
- Assumption: review trigger for sensitive paths and >3-concern PR split threshold are local safeguards adopted here.
- Self-check: all required baseline sections are present; commands/policies are evidence-backed or marked assumption; canonical capability names are used with aliases marked optional; practical fallbacks are defined; no personal local paths are included.
