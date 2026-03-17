import { useAuthStore } from '../stores/authStore'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { useState } from 'react'
import { useChatStore } from '@/stores/chatStore'

export function ProfilePage() {
  const user = useAuthStore((state) => state.user)
  const signOut = useAuthStore((state) => state.signOut)
  const clearChatMessages = useChatStore((state) => state.clearMessages);

  const [displayName, setDisplayName] = useState('')
  
  return (
    <div className="min-h-screen p-4 md:p-0 pb-[80px] md:pb-8 bg-muted/10">
      <div className="max-w-4xl mx-auto mt-4 md:mt-8">
        <h1 className="text-3xl font-bold mb-6">Profile</h1>
        
        <Card className="mb-4">
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>
              Manage your account details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Email</Label>
              <Input value={user?.email || ''} disabled />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="displayName">Display Name</Label>
              <Input
                id="displayName"
                placeholder="Enter your display name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>
            
            <Button>Save Changes</Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Danger Zone</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full">
              Change Password
            </Button>
            <Button 
              onClick={() => {
                signOut();
                clearChatMessages();
              }}
              variant="destructive" className="w-full bg-emerald-600 text-white hover:bg-emerald-700 rounded-full px-6 font-black uppercase tracking-[0.15em] text-[9px] h-10 shadow-lg shadow-emerald-100 transition-all active:scale-95">
              Sign Out
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
