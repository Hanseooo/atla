import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'

export const Route = createFileRoute('/profile/')({
  component: ProfilePage,
  beforeLoad: requireAuth,
})

function ProfilePage() {
  return <div>Profile Page</div>
}
