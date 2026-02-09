import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'
import { ChatPage } from '../pages/ChatPage'

export const Route = createFileRoute('/chat')({
  component: ChatRoute,
  beforeLoad: requireAuth,
})

function ChatRoute() {
  return <ChatPage />
}
