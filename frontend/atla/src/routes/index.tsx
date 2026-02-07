import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'

export const Route = createFileRoute('/')({
  component: HomePage,
  beforeLoad: requireAuth,
})

function HomePage() {
  return (
    <div>
      <div>Home Page - Trip Dashboard</div>
      <div>Welcome! Your trips will appear here.</div>
    </div>
  )
}
