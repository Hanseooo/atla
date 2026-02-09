import { useState, useEffect } from 'react'
import { Link } from '@tanstack/react-router'
import { useAuthStore } from '../stores/authStore'
import { useUsernameCheck } from '../hooks/useUsernameCheck'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card'
import { Alert, AlertDescription } from '../components/ui/alert'
import { Loader2, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'

interface SignupPageProps {
  onSignup?: () => void
}

export function SignupPage({ onSignup }: SignupPageProps) {
  const signUp = useAuthStore((state) => state.signUp)
  const retryProfileCreation = useAuthStore((state) => state.retryProfileCreation)
  const clearProfileError = useAuthStore((state) => state.clearProfileError)
  const isLoading = useAuthStore((state) => state.isLoading)
  const profileCreationError = useAuthStore((state) => state.profileCreationError)
  const { isAvailable, isChecking, error: usernameError, checkUsername } = useUsernameCheck(500)
  
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isRetrying, setIsRetrying] = useState(false)
  
  // Check username availability when username changes
  useEffect(() => {
    checkUsername(username)
  }, [username, checkUsername])
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    clearProfileError()
    
    // Validate username
    if (username.length < 3) {
      setError('Username must be at least 3 characters')
      return
    }
    
    if (isAvailable === false) {
      setError(usernameError || 'Username is not available')
      return
    }
    
    // Validate password match
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    // Validate password length
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    
    try {
      await signUp(email, password, username)
      setSuccess(true)
      setTimeout(() => {
        onSignup?.()
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to sign up')
    }
  }
  
  const handleRetry = async () => {
    setIsRetrying(true)
    setError('')
    clearProfileError()
    
    try {
      await retryProfileCreation()
      setSuccess(true)
      setTimeout(() => {
        onSignup?.()
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to retry profile creation')
    } finally {
      setIsRetrying(false)
    }
  }
  
  // Show profile creation error with retry option
  if (profileCreationError?.canRetry) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Almost Done!</CardTitle>
            <CardDescription className="text-center">
              We need to finish setting up your profile
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <Alert className="mb-4 border-yellow-500">
              <AlertCircle className="h-4 w-4 text-yellow-500" />
              <AlertDescription>{profileCreationError.message}</AlertDescription>
            </Alert>
            
            <Button 
              onClick={handleRetry} 
              className="w-full"
              disabled={isRetrying}
            >
              {isRetrying ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Retrying...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Retry Profile Setup
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }
  
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <CheckCircle2 className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <CardTitle className="mb-2">Success!</CardTitle>
            <CardDescription>
              Your account has been created. Redirecting you to your dashboard...
            </CardDescription>
          </CardContent>
        </Card>
      </div>
    )
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Create Account</CardTitle>
          <CardDescription className="text-center">
            Start planning your Philippine adventures today
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <div className="relative">
                <Input
                  id="username"
                  type="text"
                  placeholder="johndoe"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  minLength={3}
                  maxLength={50}
                  pattern="^[a-zA-Z0-9_]+$"
                  className={isAvailable === true ? 'border-green-500' : isAvailable === false ? 'border-red-500' : ''}
                />
                {isChecking && (
                  <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
                )}
                {isAvailable === true && !isChecking && (
                  <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-green-500" />
                )}
                {isAvailable === false && !isChecking && (
                  <AlertCircle className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-red-500" />
                )}
              </div>
              {isAvailable === false && (
                <p className="text-sm text-red-500">{usernameError}</p>
              )}
              {isAvailable === true && (
                <p className="text-sm text-green-500">Username is available!</p>
              )}
              <p className="text-xs text-muted-foreground">
                3-50 characters, letters, numbers, and underscores only
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Create a password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full"
              disabled={isLoading || isChecking || isAvailable === false}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>
        </CardContent>
        
        <CardFooter className="flex justify-center">
          <p className="text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link 
              to="/login"
              className="text-primary hover:underline font-medium"
            >
              Sign in
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  )
}
