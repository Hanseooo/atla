import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { requireGuest } from '../lib/auth-guards'
import { SignupPage } from '../pages/SignupPage'

export const Route = createFileRoute('/signup')({
  component: SignupRoute,
  beforeLoad: requireGuest,
});

function SignupRoute() {
  const navigate = useNavigate()
  
  return (
    <SignupPage 
      onSignup={() => navigate({ to: '/home' })}
    />
  )
}
