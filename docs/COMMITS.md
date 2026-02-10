# Commit Message Conventions

We follow **Conventional Commits** for clear, structured commit history that is easy to read and automate.

## Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add login page` |
| `fix` | Bug fix | `fix(routes): resolve redirect loop` |
| `docs` | Documentation changes | `docs(readme): update setup instructions` |
| `style` | Code style (formatting, semicolons) | `style(frontend): fix indentation` |
| `refactor` | Code restructuring | `refactor(api): simplify error handling` |
| `test` | Adding/updating tests | `test(auth): add unit tests` |
| `chore` | Maintenance tasks | `chore(deps): update dependencies` |
| `perf` | Performance improvements | `perf(api): optimize query` |
| `ci` | CI/CD changes | `ci(github): add test workflow` |

## Scope (Optional)

Indicate the area of change:

- `frontend` - React/TypeScript code
- `backend` - Python/FastAPI code
- `api` - API endpoints
- `db` - Database models/migrations
- `auth` - Authentication/authorization
- `ui` - UI components
- `deps` - Dependencies

## Subject Line Rules

- **Use imperative mood**: "add" not "added" or "adds"
- **Don't capitalize** first letter
- **No period** at the end
- **Keep under 50 characters** (72 max)

## Good Examples

```bash
# Feature
feat(frontend): add landing page hero section
feat(auth): implement user login with supabase

# Bug fix
fix(backend): resolve database connection timeout
fix(ui): correct button alignment on mobile

# Documentation
docs(api): document trip endpoints
docs(readme): add installation instructions

# Refactoring
refactor(backend): simplify trip repository logic
refactor(frontend): extract reusable button component

# Tests
test(backend): add unit tests for auth service
test(api): add integration tests for trip endpoints

# Maintenance
chore(deps): upgrade react to v19
chore(ci): update github actions workflow
```

## Bad Examples

```bash
Added login page                    # Wrong: No type, past tense
feat: Added Landing Page            # Wrong: Capitalized, past tense
fix: fixed the bug.                 # Wrong: Period at end, redundant
feat: updates                       # Wrong: Too vague
chore: some changes                 # Wrong: Not descriptive
```

## Body (Optional)

Explain the "why" and "what" when the subject isn't enough:

```
feat(auth): implement password reset

Add password reset flow using Supabase Auth. Users receive
email with reset link valid for 24 hours.

- Add /forgot-password route
- Add /reset-password route
- Integrate with Supabase reset API
```

**When to use body:**
- Breaking changes
- Complex features
- Why the change was made
- What alternatives were considered

## Footer (Optional)

Reference issues, PRs, or note breaking changes:

```
feat(api): add trip filtering

Closes #123
```

**Breaking changes:**
```
feat(api): change trip list response format

BREAKING CHANGE: trip list endpoint now returns paginated
response instead of full list. Update client code to handle
pagination metadata.

Closes #456
```

## Commit Best Practices

### Do:

- ✓ Make atomic commits (one logical change per commit)
- ✓ Write clear, descriptive messages
- ✓ Use body to explain "why" not just "what"
- ✓ Reference issues when applicable
- ✓ Commit early and often

### Don't:

- ✗ Commit broken code
- ✗ Mix unrelated changes in one commit
- ✗ Write vague messages like "fix stuff"
- ✗ Commit secrets or sensitive data
- ✗ Commit large binary files

## Atomic Commits

Each commit should be a single logical change:

```bash
# Good - separate concerns
git commit -m "feat(auth): add login form component"
git commit -m "feat(auth): implement login API endpoint"
git commit -m "test(auth): add login unit tests"

# Bad - everything in one
git commit -m "add auth stuff and some fixes"
```

## Commit Frequency

**Commit early, commit often:**

```bash
# After completing a small task
git add src/components/Login.tsx
git commit -m "feat(auth): add login form UI"

# After implementing functionality
git add src/lib/auth.ts
git commit -m "feat(auth): implement login logic"

# After adding tests
git add src/components/Login.test.tsx
git commit -m "test(auth): add login form tests"
```

## Amending Commits

If you make a mistake in your last commit:

```bash
# Add more changes to last commit
git add .
git commit --amend -m "feat(auth): add login form"

# Just fix the message
git commit --amend -m "new message"

# Don't amend if already pushed (unless you know what you're doing)
```

## Viewing Commit History

```bash
# Pretty log
git log --oneline --graph --decorate

# See what changed in last commit
git show

# See commits by author
git log --author="Your Name"
```

## Quick Reference

```bash
# Commit with message
git commit -m "feat(scope): description"

# Commit all modified files
git commit -am "fix: quick fix"

# Amend last commit
git commit --amend -m "new message"

# View commit history
git log --oneline -10
```

## Related Documents

- [Contributing Guide](./CONTRIBUTING.md) - Getting started with contributions
- [Branching Guide](./BRANCHING.md) - Git workflow and branch naming
- [Pull Request Guide](./PULL_REQUESTS.md) - PR process and requirements
