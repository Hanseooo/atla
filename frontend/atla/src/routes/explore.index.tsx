import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'

export const Route = createFileRoute('/explore/')({
  component: ExplorePage,
  beforeLoad: requireAuth,
})

function ExplorePage() {
  return <div>Explore Page</div>
}
