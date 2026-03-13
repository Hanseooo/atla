import { Card, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { ChatInterface } from '../components/chat/ChatInterface';

export function ChatPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background md:p-4">
      <div className="flex-1 w-full max-w-4xl mx-auto flex flex-col h-[100dvh] md:h-auto">
        <Card className="flex-1 flex flex-col border-0 rounded-none md:border md:rounded-xl md:max-h-[85vh] shadow-none md:shadow-sm overflow-hidden">
          <CardHeader className="px-4 py-3 md:p-6 border-b z-10 bg-card">
            <CardTitle className="text-lg md:text-2xl">Plan Your Trip</CardTitle>
            <CardDescription className="text-xs md:text-sm">
              Chat with our AI to plan your perfect Philippine adventure
            </CardDescription>
          </CardHeader>
          
          <ChatInterface />
          
        </Card>
      </div>
    </div>
  );
}