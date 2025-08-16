import { useEffect, useMemo, useRef, useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { useChat } from '@/hooks/use-chat'
import { useChatStore, selectMessagesBySession } from '@/stores/chat-store'
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

  useEffect(() => {
    ensureSession()
  }, [ensureSession])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages.length])

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


