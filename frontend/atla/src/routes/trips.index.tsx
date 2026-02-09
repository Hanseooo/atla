import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'
import { TripsPage } from '../pages/TripsPage'

export const Route = createFileRoute('/trips/')({
  component: TripsRoute,
  beforeLoad: requireAuth,
})

function TripsRoute() {
  return <TripsPage />
}
