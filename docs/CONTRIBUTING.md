# Contributing Guide

Welcome! This guide will help you contribute to Atla - Philippine AI Travel Planning app.

## Quick Start

### 1. Setup Your Environment

```bash
# Clone the repository
git clone <repo-url>
cd ph-travel-app

# Setup backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# Setup frontend
cd ../frontend/atla
npm install
```

### 2. Create a Branch

```bash
# Make sure you're on main and it's up to date
git checkout main
git pull origin main

# Create your feature branch
git checkout -b feat/your-feature-name
```

### 3. Make Changes

- Write your code following our [style guidelines](../AGENTS.md#code-style-guidelines)
- Run tests locally
- Ensure type checking passes

### 4. Commit

```bash
git add .
git commit -m "feat(scope): description of changes"
```

### 5. Push and Create PR

```bash
git push -u origin feat/your-feature-name
```

Then open a Pull Request on GitHub. See [Pull Requests](./PULL_REQUESTS.md) for details.

---

## Development Workflow

### Before You Start

1. **Check existing issues** - Look for something to work on
2. **Create an issue** - If you found a bug or have a feature idea
3. **Claim an issue** - Comment on it so others know you're working on it

### Making Changes

1. **Keep branches short-lived** - Merge within days, not weeks
2. **Pull main frequently** - Stay up to date to avoid conflicts
3. **Commit often** - Small, focused commits are easier to review
4. **Test locally** - Run type checks and builds before pushing

### Code Quality Checklist

Before creating a PR:

- [ ] Code follows project conventions (see [AGENTS.md](../AGENTS.md))
- [ ] Build passes (`npm run build` in frontend)
- [ ] Type check passes (`npm run typecheck` in frontend)
- [ ] Self-review completed
- [ ] No secrets or credentials in code
- [ ] Documentation updated (if needed)

---

## Merge Conflict Resolution

Conflicts happen when the same file is modified in both branches.

### Steps to Resolve

1. **Fetch latest main:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Switch to your branch:**
   ```bash
   git checkout your-feature-branch
   ```

3. **Merge main into your branch:**
   ```bash
   git merge main
   ```

4. **Resolve conflicts:**
   - Open conflicted files in your editor
   - Look for conflict markers:
     ```
     <<<<<<< HEAD
     (current branch code)
     =======
     (incoming code from main)
     >>>>>>> main
     ```
   - Edit to keep the correct code
   - Remove conflict markers

5. **Mark as resolved:**
   ```bash
   git add <resolved-files>
   git commit -m "merge: resolve conflicts with main"
   ```

6. **Push resolved branch:**
   ```bash
   git push origin your-feature-branch
   ```

### Prevention Tips

- **Pull main frequently** while working on long-running branches
- **Keep branches short-lived** (merge within days, not weeks)
- **Communicate** with team about what files you're touching

---

## Project Structure

```
ph-travel-app/
├── backend/           # FastAPI + Python
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   └── docs/         # Backend documentation
├── frontend/         # React + TypeScript
│   └── atla/        # Frontend application
│       ├── src/
│       │   ├── components/
│       │   ├── routes/
│       │   └── lib/
├── docs/            # Project documentation
└── .github/         # GitHub templates and workflows
```

---

## Resources

### Documentation

- **[Branching Guide](./BRANCHING.md)** - Git workflow and branch naming
- **[Commit Conventions](./COMMITS.md)** - How to write good commit messages
- **[Pull Request Guide](./PULL_REQUESTS.md)** - PR process and requirements
- **[Architecture Guide](./ARCHITECTURE.md)** - Code patterns and architecture
- **[AGENTS.md](../AGENTS.md)** - AI agent guidelines and code style

### Useful Commands

```bash
# Backend
cd backend && uvicorn app.main:app --reload    # Start dev server
pytest                                          # Run tests
alembic upgrade head                           # Run migrations

# Frontend
cd frontend/atla && npm run dev                # Start dev server
npm run build                                  # Production build
npm run typecheck                             # Type checking
```

---

## Getting Help

- **Stuck on something?** Create an issue with the "help wanted" label
- **Found a bug?** Create an issue with the "bug" label
- **Have a question?** Open a discussion on GitHub
- **Want to chat?** Check if we have a Discord/Slack (add link if applicable)

---

## Code of Conduct

Be respectful, constructive, and inclusive. We're all here to build something great together!

---

**Ready to contribute?** Pick an issue and dive in! 🚀
