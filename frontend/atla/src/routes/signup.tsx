import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { requireGuest } from '../lib/auth-guards'

export const Route = createFileRoute('/signup')({
  component: SignupPage,
  beforeLoad: requireGuest,
})

function SignupPage() {
  const navigate = useNavigate()
  const signUp = useAuthStore((state) => state.signUp)
  const isLoading = useAuthStore((state) => state.isLoading)
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    try {
      await signUp(email, password, username)
      setSuccess(true)
      // After successful signup, redirect to home
      // Note: If email confirmation is required, user will be redirected to login
      setTimeout(() => {
        navigate({ to: '/' })
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to sign up')
    }
  }
  
  if (success) {
    return (
      <div>
        <h1>Success!</h1>
        <p>Your account has been created. Redirecting...</p>
      </div>
    )
  }
  
  return (
    <div>
      <h1>Sign Up</h1>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating account...' : 'Sign Up'}
        </button>
      </form>
      <div>
        Already have an account? <a href="/login">Sign in</a>
      </div>
    </div>
  )
}
