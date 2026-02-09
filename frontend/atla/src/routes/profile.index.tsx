import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'
import { ProfilePage } from '../pages/ProfilePage'

export const Route = createFileRoute('/profile/')({
  component: ProfileRoute,
  beforeLoad: requireAuth,
})

function ProfileRoute() {
  return <ProfilePage />
}
