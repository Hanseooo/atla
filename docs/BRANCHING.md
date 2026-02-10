# Branching Strategy

We use **GitHub Flow** - a simple, lightweight branching strategy perfect for continuous deployment.

## The Main Branch

- **`main`** is always deployable
- All changes go through Pull Requests
- **Never commit directly to main**
- CI/CD runs on every PR to ensure quality

## Feature Branches

Create short-lived branches from main for all work:

```bash
# 1. Update main first
git checkout main
git pull origin main

# 2. Create your feature branch
git checkout -b feat/your-feature-name

# 3. Make your changes
# ... edit files ...

# 4. Commit
git add .
git commit -m "feat(scope): description"

# 5. Push
git push -u origin feat/your-feature-name

# 6. Create Pull Request on GitHub
```

## Branch Naming Convention

Use **slash notation** with descriptive names:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New features | `feat/user-authentication` |
| `fix/` | Bug fixes | `fix/login-redirect-loop` |
| `docs/` | Documentation | `docs/api-endpoints` |
| `chore/` | Maintenance | `chore/update-dependencies` |
| `refactor/` | Code refactoring | `refactor/simplify-auth` |
| `test/` | Adding tests | `test/auth-service` |
| `hotfix/` | Urgent production fixes | `hotfix/security-patch` |

### Naming Rules

- Use lowercase letters and hyphens
- Keep it descriptive but concise (3-5 words max)
- Include issue number if applicable: `feat/123-user-auth`

### Good Examples

```bash
feat/landing-page-hero
fix/navbar-mobile-responsive
docs/contributing-guidelines
refactor/simplify-trip-repository
```

### Bad Examples

```bash
feature-new-stuff              # Wrong prefix (use feat/)
fix_login_bug                  # Underscores instead of hyphens
my-branch                      # No type prefix
feat/very-long-branch-name-that-is-hard-to-read  # Too long
```

## Branch Lifecycle

```
1. CREATE    → Create branch from main
2. DEVELOP   → Work on your feature/fix
3. PUSH      → Push branch to GitHub
4. PR        → Create Pull Request
5. REVIEW    → Address feedback (if any)
6. MERGE     → Merge to main
7. DELETE    → Delete branch after merge
```

### 1. Create

Always create from updated main:

```bash
git checkout main
git pull origin main
git checkout -b feat/my-feature
```

### 2. Develop

- Make focused, atomic commits
- Test locally before pushing
- Keep the branch focused on one feature/fix

### 3. Push

```bash
git push -u origin feat/my-feature
```

### 4. Create PR

See [Pull Requests](./PULL_REQUESTS.md) for details.

### 5. Review

- Address any feedback
- Make requested changes
- Re-request review if needed

### 6. Merge

- CI must pass
- Reviewer decides: squash or preserve commits

### 7. Delete

Delete your branch after merging:

```bash
git checkout main
git pull origin main
git branch -d feat/my-feature  # Delete local branch
```

## Branch Workflow Diagram

```
main (always deployable)
  │
  │ git checkout -b feat/feature-name
  ▼
feat/feature-name (your work)
  │
  │ git push + Create PR
  ▼
Pull Request (review + CI)
  │
  │ Merge
  ▼
main (updated with your changes)
```

## Quick Reference Commands

```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feat/my-feature

# Update branch with latest main
git checkout main
git pull origin main
git checkout feat/my-feature
git merge main

# Clean up after merge
git checkout main
git pull origin main
git branch -d feat/my-feature  # Delete local branch

# List all branches
git branch -a

# Check which branch you're on
git branch
```

## Best Practices

- **Keep branches short-lived** - Merge within days, not weeks
- **Pull main frequently** - Stay up to date while working
- **One feature per branch** - Don't mix unrelated changes
- **Use descriptive names** - Others (and future you) should understand the purpose
- **Delete merged branches** - Keep the repository clean

## Related Documents

- [Contributing Guide](./CONTRIBUTING.md) - Getting started with contributions
- [Commit Conventions](./COMMITS.md) - How to write commit messages
- [Pull Request Guide](./PULL_REQUESTS.md) - PR process and requirements
