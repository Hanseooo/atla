import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'

export const Route = createFileRoute('/trips/')({
  component: TripsPage,
  beforeLoad: requireAuth,
})

function TripsPage() {
  return <div>Trips List Page</div>
}
