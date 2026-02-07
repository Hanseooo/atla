import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'

export const Route = createFileRoute('/trips/$tripId')({
  component: TripDetailPage,
  beforeLoad: requireAuth,
})

function TripDetailPage() {
  const { tripId } = Route.useParams()
  
  return (
    <div>
      <div>Trip Detail Page</div>
      <div>Trip ID: {tripId}</div>
    </div>
  )
}
