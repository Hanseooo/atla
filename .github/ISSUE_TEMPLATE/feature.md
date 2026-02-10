---
name: Feature Request
description: Suggest a new feature or enhancement for the project
title: '[Feature]: '
labels: ['enhancement', 'triage']
assignees: []
---

## Feature Summary
<!-- Provide a clear and concise description of the feature -->

## User Story
<!-- Describe who will use this feature and why -->
As a **[type of user]**, I want **[goal]** so that **[benefit]**.

## Acceptance Criteria
<!-- List the specific requirements that must be met for this feature to be considered complete -->
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Requirements
<!-- Detail the technical implementation requirements -->

### Files to Create/Modify
<!-- List specific files that need to be created or modified -->
- `src/path/to/file.tsx` - Description
- `src/path/to/hook.ts` - Description

### Dependencies
<!-- List any new dependencies that need to be installed -->
```bash
npm install package-name
npx shadcn add component-name
```

### API Endpoints
<!-- If this feature requires backend integration, list the endpoints -->
- `GET /api/endpoint` - Description
- `POST /api/endpoint` - Description

## Architecture Notes
<!-- Reference the project architecture patterns that should be followed -->

### Route Structure (if applicable)
<!-- Follow TanStack Router file-based routing conventions -->
- Route: `/path` → File: `src/routes/path.tsx`
- Page component: `src/pages/PageName.tsx`

### State Management
<!-- Specify which state management approach to use -->
- [ ] Server State (TanStack Query) - for API data
- [ ] Client State (Zustand) - for UI state
- [ ] Local State (useState) - for component-only state

### Component Pattern
<!-- Follow the established component patterns -->
- [ ] Create page component in `src/pages/`
- [ ] Create route wrapper in `src/routes/`
- [ ] Create reusable component in `src/components/`
- [ ] Create custom hook in `src/hooks/`

## Design Specifications
<!-- Include design requirements, mockups, or styling guidelines -->

### UI/UX Requirements
- [ ] Responsive design (mobile-first)
- [ ] Accessibility (ARIA labels, keyboard navigation)
- [ ] Loading states
- [ ] Error handling

### Styling
<!-- Specify styling approach -->
- Use Tailwind CSS utility classes
- Follow shadcn/ui component patterns
- Maintain consistent spacing and typography

## Definition of Done
<!-- Checklist for when the feature is considered complete -->
- [ ] Feature implemented according to acceptance criteria
- [ ] TypeScript types defined (no `any` types)
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] Responsive design tested
- [ ] Code follows project conventions (see ARCHITECTURE.md)
- [ ] Build passes (`npm run build`)
- [ ] Type check passes (`npm run typecheck`)
- [ ] Self-review completed
- [ ] Documentation updated (if applicable)

## Additional Context
<!-- Add any other context, screenshots, or examples about the feature request here -->

## Related Issues
<!-- Link to any related issues or PRs -->
- Related to #issue-number
- Depends on #issue-number

## Estimated Effort
<!-- Optional: Rough estimate of implementation time -->
- [ ] Small (1-2 days)
- [ ] Medium (3-5 days)
- [ ] Large (1+ weeks)
