import { useEffect, useMemo, useRef, useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { useChat } from '@/hooks/use-chat'
import { useChatStore, selectMessagesBySession } from '@/stores/chat-store'
import ChatMessage from '@/components/chat/ChatMessage'
import ChatInput from '@/components/chat/ChatInput'
import ModelSelector from '@/components/chat/ModelSelector'

export function ChatContainer() {
  const { sessionId } = useParams({ from: '/chat/$sessionId' })
  const { sendMessage, ensureSession } = useChat(sessionId)
  const messages = useChatStore(useMemo(() => selectMessagesBySession(sessionId), [sessionId]))
  const [model, setModel] = useState('gpt-4o')
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
        <div ref={bottomRef} />
      </div>
      <div className="mt-3">
        <ChatInput onSubmit={(text) => sendMessage(text, model)} />
      </div>
    </div>
  )
}

export default ChatContainer


