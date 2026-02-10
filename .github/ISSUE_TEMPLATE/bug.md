---
name: Bug Report
about: A structured template for reporting bugs with clear steps, expected vs actual
  behavior, logs, and environment details to help diagnose and fix issues faster
title: "[Bug]: "
labels: bug
assignees: ''

---

## Bug Description
<!-- Provide a clear and concise description of the bug -->

## Steps to Reproduce
<!-- List the exact steps to reproduce the bug -->
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
<!-- Describe what you expected to happen -->

## Actual Behavior
<!-- Describe what actually happened -->

## Screenshots / Logs
<!-- If applicable, add screenshots or error logs to help explain the problem -->

### Console Errors
```
Paste any error messages from the browser console here
```

### Network Errors
<!-- If applicable, include network request/response details -->
- Endpoint: `GET /api/endpoint`
- Status: 500
- Response: `{ "error": "..." }`

## Environment
<!-- Provide details about your environment -->

### Frontend
- **OS**: [e.g., Windows 10, macOS 13, Ubuntu 22.04]
- **Browser**: [e.g., Chrome 120, Firefox 121, Safari 17]
- **Node Version**: [e.g., 20.10.0] (run `node --version`)
- **Branch/Commit**: [e.g., main@abc1234]

### Backend (if applicable)
- **Python Version**: [e.g., 3.11.0]
- **Database**: [e.g., Supabase, PostgreSQL 15]

## Severity
<!-- Select the severity level -->
- [ ] 🔴 Critical - App crashes, data loss, security vulnerability
- [ ] 🟠 High - Major feature broken, significant impact
- [ ] 🟡 Medium - Feature partially broken, workaround exists
- [ ] 🟢 Low - Minor issue, cosmetic, or edge case

## Frequency
<!-- How often does this bug occur? -->
- [ ] Always (100% of the time)
- [ ] Often (more than 50% of the time)
- [ ] Sometimes (less than 50% of the time)
- [ ] Rarely (hard to reproduce)

## Additional Context
<!-- Add any other context about the problem here -->
- Does it happen in incognito/private mode?
- Does clearing cache fix it?
- Does it happen on other devices/browsers?
- Any recent changes (deployments, updates)?

## Possible Solution
<!-- If you have ideas on how to fix this bug, describe them here -->

## Related Issues
<!-- Link to any related issues -->
- Related to #issue-number
- Duplicate of #issue-number
