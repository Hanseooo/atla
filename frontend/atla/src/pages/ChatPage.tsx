import { Card, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { ChatInterface } from '../components/chat/ChatInterface';

export function ChatPage() {
  return (
    <div className="min-h-[80vh] sm:min-h-0 flex flex-col bg-background md:mt-5 pb-20 md:pb-0">
      <div className="flex-1 w-full max-w-4xl mx-auto flex flex-col h-[calc(100dvh-64px)] md:h-auto overflow-hidden">
        <Card className="flex-1 flex flex-col border-0 rounded-none md:border md:rounded-xl md:max-h-[85vh] shadow-none md:shadow-sm overflow-hidden relative px-3 md:px-0">
          <CardHeader className="px-0 md:px-6 [.border-b]:pb-4 border-b z-10 bg-card">
            <CardTitle className="text-2xl">Plan Your Trip</CardTitle>
            <CardDescription className="text-sm">
              Chat with our AI to plan your perfect Philippine adventure
            </CardDescription>
          </CardHeader>
          
          <ChatInterface />
          
        </Card>
      </div>
    </div>
  );
}