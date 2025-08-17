import { useEffect, useMemo, useRef, useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { useChat } from '@/hooks/use-chat'
import { useChatStore, selectMessagesBySession } from '@/stores/chat-store'
import { useAuthStore } from '@/stores/auth'
import ChatMessage from '@/components/chat/ChatMessage'
import ChatInput from '@/components/chat/ChatInput'
import ModelSelector from '@/components/chat/ModelSelector'
import GenerationControls from '@/components/slides/GenerationControls'

export function ChatContainer() {
  console.log('ChatContainer rendering')
  const { sessionId } = useParams({ from: '/chat/$sessionId' })
  console.log('sessionId:', sessionId)
  const { sendMessage, ensureSession } = useChat(sessionId)
  const messages = useChatStore(useMemo(() => selectMessagesBySession(sessionId), [sessionId]))
  const [model, setModel] = useState('openai/gpt-4o-mini')
  const bottomRef = useRef<HTMLDivElement | null>(null)
  
  // Authentication
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const login = useAuthStore((state) => state.login)
  const [loginEmail, setLoginEmail] = useState('test@example.com')
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  useEffect(() => {
    ensureSession()
  }, [ensureSession])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages.length])

  const handleLogin = async () => {
    setIsLoggingIn(true)
    try {
      await login(loginEmail)
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setIsLoggingIn(false)
    }
  }

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="mx-auto flex h-[calc(100vh-7rem)] max-w-3xl flex-col items-center justify-center">
        <div className="w-full max-w-md space-y-4 rounded-lg border p-6 dark:border-gray-800">
          <h2 className="text-xl font-semibold">Login Required</h2>
          <p className="text-sm text-muted-foreground">
            Please login to use the PowerPoint generation features.
          </p>
          <div className="space-y-2">
            <input
              type="email"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              placeholder="Enter your email"
              className="w-full rounded border px-3 py-2 dark:border-gray-700 dark:bg-gray-800"
            />
            <button
              onClick={handleLogin}
              disabled={isLoggingIn}
              className="w-full rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoggingIn ? 'Logging in...' : 'Login'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-7rem)] max-w-3xl flex-col">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-lg font-semibold">Session: {sessionId}</div>
        <ModelSelector value={model} onChange={setModel} />
      </div>
      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto rounded border p-3 dark:border-gray-800">
        {messages.map((m) => (
          <ChatMessage
            key={m.id}
            role={m.role}
            content={m.content}
            createdAt={m.createdAt}
            pending={m.status === 'pending'}
            slides={m.slides as any}
          />
        ))}
        {/* Generation controls appear when the latest assistant message contains slides */}
        {(() => {
          const lastAssistantWithSlides = [...messages]
            .reverse()
            .find((m) => m.role === 'assistant' && Array.isArray(m.slides) && m.slides.length > 0)
          if (!lastAssistantWithSlides) return null
          const outline = (lastAssistantWithSlides.slides as any[]).map((s) => ({
            title: s.title as string,
            bullets: Array.isArray(s.bullets) ? (s.bullets as string[]) : [],
            // Preserve detailed speaker notes for full, non-truncated content in notes pane
            speaker_notes: typeof (s as any).notes === 'string' ? ((s as any).notes as string) : undefined,
            // Pass through image prompt for image generation
            image_prompt: typeof (s as any).image === 'string' ? ((s as any).image as string) : undefined,
          }))
          return (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Ready to build PowerPoint:</span>
              <GenerationControls outline={outline} sessionId={sessionId} />
            </div>
          )
        })()}
        <div ref={bottomRef} />
      </div>
      <div className="mt-3">
        <ChatInput onSubmit={(text) => sendMessage(text, model)} />
      </div>
    </div>
  )
}

export default ChatContainer


