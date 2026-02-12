import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'
import { HomePage } from '../pages/HomePage'

export const Route = createFileRoute('/home')({
  component: HomeRoute,
  beforeLoad: requireAuth,
})

function HomeRoute() {
  return <HomePage />
}
