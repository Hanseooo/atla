import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'
import { TripDetailPage } from '../pages/TripDetailPage'

export const Route = createFileRoute('/trips/$tripId')({
  component: TripDetailRoute,
  beforeLoad: requireAuth,
})

function TripDetailRoute() {
  return <TripDetailPage />
}
