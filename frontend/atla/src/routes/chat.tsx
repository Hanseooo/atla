import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'

export const Route = createFileRoute('/chat')({
  component: ChatPage,
  beforeLoad: requireAuth,
})

function ChatPage() {
  return <div>Chat Page</div>
}
