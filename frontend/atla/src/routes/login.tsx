import { createFileRoute, useNavigate, useSearch } from '@tanstack/react-router'
import { requireGuest } from '../lib/auth-guards'
import { LoginPage } from '../pages/LoginPage'

export const Route = createFileRoute('/login')({
  component: LoginRoute,
  beforeLoad: requireGuest,
});

function LoginRoute() {
  const navigate = useNavigate()
  const search = useSearch({ from: '/login' })
  const redirectTo = (search as any).redirect || '/home'
  
  return (
    <LoginPage 
      redirectTo={redirectTo}
      onLogin={() => navigate({ to: redirectTo })}
    />
  )
}
