# Frontend CI Pipeline

This document describes the GitHub Actions CI pipeline for the Philippine Travel App frontend.

## Overview

The CI pipeline runs on every pull request to ensure code quality and catch issues before merging.

## Triggers

The pipeline runs on:
- Pull requests to `main` branch
- Pull requests to `develop` branch
- Only when files in `frontend/atla/**` or the workflow itself change

## Jobs

The pipeline runs 3 jobs in parallel for fast feedback:

### 1. Lint
- Runs ESLint to check code style and catch potential bugs
- Uses the project's ESLint configuration
- Fails on any linting errors

### 2. Type Check
- Runs TypeScript compiler to check for type errors
- Uses `tsc --noEmit` (doesn't generate build files)
- Fails on any type errors

### 3. Build
- Builds the application with Vite
- Verifies the production build succeeds
- Uses environment variables from GitHub Secrets

### 4. Summary
- Checks status of all previous jobs
- Provides clear pass/fail status
- Required for PR merge (branch protection)

## Node.js Version

We use **Node.js 20 LTS**:
- Long-term support until April 2026
- Stable and battle-tested
- Good ecosystem compatibility
- Defined in `.nvmrc` for local development consistency

## Caching

Caching is enabled for npm dependencies:
- Cuts build time by ~60% on subsequent runs
- Caches `node_modules` based on `package-lock.json`
- Automatically invalidated when dependencies change

## Environment Variables

The following secrets must be configured in GitHub:

| Secret | Description | Required For |
|--------|-------------|--------------|
| `VITE_SUPABASE_URL` | Supabase project URL | Build |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key | Build |
| `VITE_API_URL` | Backend API URL | Build |

### Setting Up Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its value

Example values:
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_API_URL=http://localhost:8000
```

## Local Development

To ensure consistency with CI:

```bash
# Use the correct Node version (if using nvm)
nvm use

# Or install the version specified in .nvmrc
nvm install 20

# Install dependencies
npm ci

# Run checks locally before pushing
npm run lint
npm run typecheck
npm run build
```

## Workflow File

The workflow is defined in `.github/workflows/frontend-ci.yml`.

### Key Features

- **Parallel execution**: All checks run simultaneously for fast feedback
- **Path filtering**: Only runs when frontend files change
- **Concurrency control**: Cancels previous runs if new commits are pushed
- **Clear status**: Each job reports separately in PR checks

## Troubleshooting

### Job fails with "Cannot find module"

Make sure all dependencies are in `package.json` and committed:
```bash
rm -rf node_modules package-lock.json
npm install
npm ci  # Verify lock file is valid
```

### Type check fails but builds locally

Check TypeScript version:
```bash
npx tsc --version
```

Ensure it's the same version specified in `package.json`.

### Build fails with environment variable errors

Verify all required secrets are set in GitHub repository settings.

## Branch Protection

To require CI to pass before merging:

1. Go to **Settings** → **Branches**
2. Click **Add rule** (or edit existing)
3. Enable **Require status checks to pass**
4. Search for and select:
   - `Frontend CI / Lint`
   - `Frontend CI / Type Check`
   - `Frontend CI / Build`
   - `Frontend CI / CI Summary`
5. Save changes

This ensures PRs cannot be merged until all checks pass.

## Customization

### Adding More Checks

To add a new job (e.g., unit tests):

```yaml
  test:
    name: Unit Tests
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend/atla
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/atla/package-lock.json
      - run: npm ci
      - run: npm test
```

Then update the `needs` in the summary job:
```yaml
needs: [lint, type-check, build, test]
```

### Changing Node Version

1. Update `.nvmrc`:
   ```
   21
   ```

2. Update `.github/workflows/frontend-ci.yml`:
   ```yaml
   node-version: '21'
   ```

3. Test locally before committing

## Performance

Typical run times:
- **First run (no cache)**: ~2-3 minutes
- **Cached run**: ~1 minute
- **Parallel jobs**: All complete within 30 seconds of each other

## Questions?

See the workflow file at `.github/workflows/frontend-ci.yml` or check the Actions tab in your GitHub repository for run history.
