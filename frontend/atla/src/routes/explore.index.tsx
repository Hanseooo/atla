import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'
import { ExplorePage } from '../pages/ExplorePage'

export const Route = createFileRoute('/explore/')({
  component: ExploreRoute,
  beforeLoad: requireAuth,
})

function ExploreRoute() {
  return <ExplorePage />
}
