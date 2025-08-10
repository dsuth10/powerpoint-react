import { useCallback } from 'react'
import { useChatStore, ChatMessage } from '@/stores/chat-store'
import { useGenerateOutline } from '@/hooks/api/chat'

export function useChat(sessionId?: string) {
  const startSession = useChatStore((s) => s.startSession)
  const continueSession = useChatStore((s) => s.continueSession)
  const addMessage = useChatStore((s) => s.addMessage)
  const updateMessage = useChatStore((s) => s.updateMessage)
  const removeMessage = useChatStore((s) => s.removeMessage)

  const ensureSession = useCallback(() => {
    if (sessionId) {
      continueSession(sessionId)
      return sessionId
    }
    return startSession()
  }, [continueSession, startSession, sessionId])

  const genMutation = useGenerateOutline()

  const sendMessage = useCallback(
    async (content: string, model?: string) => {
      const id = crypto.randomUUID()
      const sid = ensureSession()
      const userMsg: ChatMessage = {
        id,
        sessionId: sid,
        role: 'user',
        content,
        createdAt: Date.now(),
        status: 'pending',
      }
      addMessage(userMsg)
      try {
        const res = await genMutation.mutateAsync({ prompt: content, model, slideCount: 5 })
        updateMessage(sid, id, (m) => {
          m.status = 'sent'
        })
        // Append assistant message with outline or text response
        addMessage({
          id: crypto.randomUUID(),
          sessionId: sid,
          role: 'assistant',
          content: typeof res === 'string' ? res : JSON.stringify(res, null, 2),
          createdAt: Date.now(),
          status: 'sent',
        })
      } catch (e) {
        updateMessage(sid, id, (m) => {
          m.status = 'error'
        })
        addMessage({
          id: crypto.randomUUID(),
          sessionId: sid,
          role: 'system',
          content: e instanceof Error ? e.message : 'Failed to generate outline',
          createdAt: Date.now(),
          status: 'sent',
        })
      }
    },
    [addMessage, ensureSession, genMutation, updateMessage],
  )

  return { ensureSession, sendMessage, startSession, continueSession, addMessage, updateMessage, removeMessage, genMutation }
}


