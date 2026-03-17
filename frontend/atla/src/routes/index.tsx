import LandingPage from '@/pages/LandingPage';
import { createFileRoute } from '@tanstack/react-router'
import { redirectAuthenticated } from '../lib/auth-guards'

export const Route = createFileRoute('/')({
  beforeLoad: redirectAuthenticated,
  component: LandingRoute,
});

function LandingRoute() {
  return <LandingPage />
}
