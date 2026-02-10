# Pull Request Guide

This guide explains how to create, review, and merge Pull Requests.

## Creating a Pull Request

### 1. Push Your Branch

```bash
git push -u origin feat/your-feature-name
```

### 2. Open PR on GitHub

1. Go to your repository on GitHub
2. Click **"Pull requests"** → **"New pull request"**
3. Select:
   - **base:** `main`
   - **compare:** `your-branch-name`
4. Fill out the PR template
5. Create the Pull Request

### 3. PR Template

The template will automatically populate. Fill out:

- **Description** - What changes and why
- **Type of Change** - Bug fix, feature, docs, etc.
- **Testing** - How you tested it
- **Screenshots** - If UI changes (optional but helpful)
- **Checklist** - Ensure everything is complete

## PR Requirements

### Must Pass ✅

Before merging, your PR must:

1. **CI Build Pass**
   - TypeScript compilation (`npm run typecheck` for frontend)
   - Production build (`npm run build` for frontend)
   - Tests pass (when configured)

2. **No Merge Conflicts**
   - Branch is up to date with `main`
   - Resolve conflicts locally if needed

### No Required Reviewers

- PRs can be merged without review
- Review is encouraged but **not required**
- Complex changes should seek review

## CI/CD Pipeline

Our GitHub Actions workflow runs on every PR:

### Jobs Performed

1. **Frontend Build**
   - TypeScript compilation
   - Vite production build
   - **Note:** Lint checks are disabled (shadcn compatibility)

2. **Backend Checks**
   - Python syntax validation
   - Import checking
   - pytest (when tests exist)

### Pipeline Flow

```
Push to PR branch
       ↓
GitHub Actions Triggered
       ↓
┌─────────────────┐
│  Build Frontend │
│  - TypeScript   │
│  - Vite build   │
└────────┬────────┘
         │
┌────────▼────────┐
│  Build Backend  │
│  - Python       │
│  - pytest       │
└────────┬────────┘
         │
    [Pass?]
    /      \
   Yes      No
   /          \
  ↓            ↓
Merge       Fix Issues
Allowed     & Retry
```

### Viewing Results

Check the Actions tab on GitHub or the status checks on your PR page.

**If CI fails:**
1. Click on the failed check to see logs
2. Fix the issue locally
3. Push the fix
4. CI will re-run automatically

## Review Process

### Getting Review (Optional)

For complex changes, request review:

1. Click **"Reviewers"** on the right side of the PR
2. Select team members
3. Wait for feedback

### Addressing Feedback

1. Make requested changes
2. Commit with descriptive messages
3. Push to the same branch
4. Changes appear automatically in the PR
5. Re-request review if needed

### What Reviewers Look For

- Code follows project conventions
- Logic is correct
- Edge cases are handled
- No obvious bugs
- Tests are appropriate

## Merging

### Who Decides?

**The reviewer/merger decides** the merge strategy.

### Merge Options

#### 1. Squash and Merge (Recommended)

Combines all commits into one clean commit.

**When to use:**
- Feature has many small "work in progress" commits
- You want clean, logical history in main

**Result:**
```
main: A → B → C → D (squashed feature)
```

#### 2. Create Merge Commit

Preserves all individual commits.

**When to use:**
- Each commit is meaningful and complete
- You want full development history

**Result:**
```
main: A → B → C → M (merge commit)
                  ↘
feature:          D → E → F
```

### Never Do

- ❌ Force push to main
- ❌ Rewrite history on shared branches
- ❌ Merge broken code
- ❌ Merge without passing CI

## After Merging

### 1. Delete Your Branch

GitHub will offer to delete the branch after merge. Click **"Delete branch"**.

Or locally:
```bash
git checkout main
git pull origin main
git branch -d feat/your-feature  # Delete local branch
```

### 2. Verify in Production

- Check that the feature works
- Monitor for any issues
- Be ready to revert if needed

### 3. Close Related Issues

If your PR fixes an issue:
- Use "Closes #123" in PR description
- GitHub will auto-close the issue on merge

## Common Issues

### "This branch is out-of-date with the base branch"

Update your branch:
```bash
git checkout main
git pull origin main
git checkout your-branch
git merge main
# Resolve conflicts if any
git push
```

### CI Build Fails

1. Check the error logs in GitHub Actions
2. Run the failing command locally:
   ```bash
   cd frontend/atla && npm run typecheck
   cd backend && pytest
   ```
3. Fix and push

### "Can't automatically merge"

Resolve conflicts locally (see [Contributing Guide](./CONTRIBUTING.md) for steps).

## Quick Reference

```bash
# Push branch and create PR
git push -u origin feat/my-feature

# Update branch with main
git checkout main
git pull origin main
git checkout feat/my-feature
git merge main

# Clean up after merge
git checkout main
git pull origin main
git branch -d feat/my-feature
```

## Workflow Summary

```
1. Create branch from main
2. Make changes and commit
3. Push to GitHub
4. Open Pull Request
5. Wait for CI (must pass)
6. Get review (optional)
7. Merge to main
8. Delete branch
9. Verify in production
```

## Related Documents

- [Contributing Guide](./CONTRIBUTING.md) - Getting started with contributions
- [Branching Guide](./BRANCHING.md) - Git workflow and branch naming
- [Commit Conventions](./COMMITS.md) - How to write commit messages
