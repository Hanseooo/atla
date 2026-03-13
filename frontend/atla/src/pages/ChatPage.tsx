import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { useState, useRef, useEffect } from 'react'
import { useSendMessage, useSubmitClarification } from '../hooks/useChat'
import { useChatStore } from '../stores/chatStore'
import { Alert, AlertDescription } from '../components/ui/alert'
import { getErrorMessage } from '../lib/api'
import { isClarificationResponse, isItineraryResponse, type ChatResponse } from '../types/chat'
import { MapPin, Calendar, Wallet, Users, ArrowRight } from 'lucide-react'

export function ChatPage() {
  const [input, setInput] = useState('')
  const { messages, addMessage, sessionId, setSessionId } = useChatStore()
  const scrollRef = useRef<HTMLDivElement>(null)
  
  const sendMessageMutation = useSendMessage()
  const submitClarificationMutation = useSubmitClarification()

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, sendMessageMutation.isPending, submitClarificationMutation.isPending])
  
  const formatAnswer = (answer: unknown): string => {
    if (typeof answer === 'string') return answer
    if (typeof answer === 'number' || typeof answer === 'boolean') return String(answer)
    if (Array.isArray(answer)) return answer.join(', ')
    if (answer && typeof answer === 'object') return JSON.stringify(answer)
    return 'Provided answer'
  }

  const handleProcessResponse = (response: ChatResponse) => {
    // Update session ID if it's a new session
    if (response.type !== 'error' && response.session_id && response.session_id !== sessionId) {
      setSessionId(response.session_id)
    }

    if (response.type === 'error') {
      addMessage({ role: 'assistant', content: `Error: ${response.message}` })
    } else {
      // Both clarification and itinerary have a message field, store the full response in data
      addMessage({ role: 'assistant', content: response.message, data: response })
    }
  }

  const handleSend = async () => {
    if (!input.trim() || sendMessageMutation.isPending) return
    
    const userMessage = input.trim()
    setInput('')
    addMessage({ role: 'user', content: userMessage })
    
    try {
      const response = await sendMessageMutation.mutateAsync({
        message: userMessage,
        session_id: sessionId || undefined,
      })
      handleProcessResponse(response)
    } catch (error: unknown) {
      addMessage({ role: 'assistant', content: `Sorry, an error occurred: ${getErrorMessage(error)}` })
    }
  }

  const handleAnswerQuestion = async (field: string, answer: unknown) => {
    if (!sessionId || submitClarificationMutation.isPending) return

    // Display the user's answer in the chat
    addMessage({ role: 'user', content: formatAnswer(answer) })

    try {
      const response = await submitClarificationMutation.mutateAsync({
        sessionId,
        answers: { [field]: answer },
      })
      handleProcessResponse(response)
    } catch (error: unknown) {
      addMessage({ role: 'assistant', content: `Sorry, an error occurred: ${getErrorMessage(error)}` })
    }
  }
  
  const isPending = sendMessageMutation.isPending || submitClarificationMutation.isPending;

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex-1 max-w-4xl mx-auto w-full p-4">
        <Card className="h-full flex flex-col max-h-[80vh]">
          <CardHeader>
            <CardTitle>Plan Your Trip</CardTitle>
            <CardDescription>
              Chat with our AI to plan your perfect Philippine adventure
            </CardDescription>
          </CardHeader>
          
          <CardContent 
            className="flex-1 overflow-y-auto space-y-4"
            ref={scrollRef}
          >
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <p>Try saying:</p>
                <p className="mt-2">"I want to visit Palawan for 3 days"</p>
              </div>
            ) : (
              messages.map((msg, i) => {
                const isClarification = msg.data && isClarificationResponse(msg.data);
                const isItinerary = msg.data && isItineraryResponse(msg.data);
                // Check if this is the latest assistant message (to avoid re-rendering old buttons)
                const isLatestAssistant = i === messages.length - 1 && msg.role === 'assistant';

                return (
                  <div key={i} className="flex flex-col gap-2">
                    <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div
                        className={`max-w-[80%] rounded-lg px-4 py-2 whitespace-pre-wrap ${
                          msg.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        {msg.content}
                      </div>
                    </div>
                    
                    {/* Render Clarification Options if it's a clarification response and it's the latest message */}
                    {isClarification && isLatestAssistant && msg?.data?.type === 'clarification' && msg.data.questions && (
                      <div className="flex flex-col items-start gap-3 mt-2 ml-4">
                        {msg.data.questions.map((question) => (
                          <div key={question.id} className="bg-card border rounded-lg p-4 w-full max-w-[80%] shadow-sm">
                            <p className="font-medium mb-3">{question.question}</p>
                            
                            {question.type === 'single_choice' && question.options && (
                              <div className="flex flex-wrap gap-2">
                                {question.options.map((opt) => (
                                  <Button 
                                    key={opt.id} 
                                    variant="outline" 
                                    size="sm"
                                    onClick={() => handleAnswerQuestion(question.field, opt.id)}
                                    disabled={isPending}
                                  >
                                    {opt.label}
                                  </Button>
                                ))}
                              </div>
                            )}
                            
                            {/* We can add handling for other types of questions (text, multiple_choice) here later */}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Render Itinerary Summary if it's an itinerary response */}
                    {isItinerary && msg?.data?.type === 'itinerary' && (
                      <div className="flex flex-col items-start mt-2 ml-4 w-full max-w-[90%]">
                        <Card className="w-full bg-primary/5 border-primary/20">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-xl flex items-center gap-2">
                              <MapPin className="h-5 w-5 text-primary" />
                              Your Trip to {msg.data.destination}
                            </CardTitle>
                            <CardDescription>
                              I've put together a complete itinerary based on your preferences!
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="flex flex-wrap gap-4 text-sm">
                              <div className="flex items-center gap-1.5 bg-background px-3 py-1.5 rounded-full border shadow-sm">
                                <Calendar className="h-4 w-4 text-muted-foreground" />
                                <span>{msg.data.days} Days</span>
                              </div>
                              {msg.data.budget && (
                                <div className="flex items-center gap-1.5 bg-background px-3 py-1.5 rounded-full border shadow-sm">
                                  <Wallet className="h-4 w-4 text-muted-foreground" />
                                  <span className="capitalize">{msg.data.budget} Budget</span>
                                </div>
                              )}
                              {msg.data.companions && (
                                <div className="flex items-center gap-1.5 bg-background px-3 py-1.5 rounded-full border shadow-sm">
                                  <Users className="h-4 w-4 text-muted-foreground" />
                                  <span className="capitalize">{msg.data.companions}</span>
                                </div>
                              )}
                            </div>

                            <div className="bg-background p-4 rounded-lg border shadow-sm space-y-3">
                              <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">Highlights</h4>
                              <ul className="space-y-2">
                                {msg.data.highlights.map((highlight: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2 text-sm">
                                    <div className="mt-1 h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
                                    <span>{highlight}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>

                            {msg.data.estimated_cost && (
                              <div className="text-sm font-medium pt-2">
                                Estimated Total: {msg.data.estimated_cost.currency || 'P'}
                                {msg.data.estimated_cost.total_min?.toLocaleString()} - {msg.data.estimated_cost.total_max?.toLocaleString()}
                              </div>
                            )}
                          </CardContent>
                          <CardFooter>
                            <Button className="w-full sm:w-auto" type="button">
                              View Full Itinerary Details <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                          </CardFooter>
                        </Card>
                      </div>
                    )}
                  </div>
                )
              })
            )}
            
            {isPending && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-lg px-4 py-2 bg-muted text-muted-foreground animate-pulse">
                  AI is thinking...
                </div>
              </div>
            )}
            
            {(sendMessageMutation.isError || submitClarificationMutation.isError) && (
              <Alert variant="destructive" className="mt-4">
                <AlertDescription>
                  {getErrorMessage(sendMessageMutation.error ?? submitClarificationMutation.error)}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
          
          <div className="p-4 border-t mt-auto">
            <div className="flex gap-2">
              <Input
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                disabled={isPending}
              />
              <Button 
                onClick={handleSend}
                disabled={isPending || !input.trim()}
              >
                Send
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
