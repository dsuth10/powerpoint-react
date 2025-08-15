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
        const res = await genMutation.mutateAsync({ 
          prompt: content, 
          model, 
          slideCount: 5,
          language: 'en'
        })
        updateMessage(sid, id, (m) => {
          m.status = 'sent'
        })
        // Append assistant message with outline or text response
        type ImageMeta = { url: string; altText?: string | null }
        type Slide = { title: string; bullets?: string[]; image?: string | ImageMeta | null; notes?: string | null }
        const slidesToMarkdown = (slides: Slide[]) =>
          slides
            .map((s, i) => {
              const parts: string[] = []
              parts.push(`### Slide ${i + 1}: ${s.title}`)
              if (s.image) {
                const url = typeof s.image === 'string' ? s.image : (s.image as ImageMeta).url
                const alt = typeof s.image === 'string' ? s.title : (s.image as ImageMeta).altText || s.title
                if (url) parts.push(`![${alt}](${url})`)
              }
              if (s.bullets && s.bullets.length) parts.push(s.bullets.map((b) => `- ${b}`).join('\n'))
              if (s.notes) parts.push(`> ${s.notes}`)
              return parts.join('\n')
            })
            .join('\n\n')

        const slidesArray = Array.isArray(res)
          ? (res as Slide[])
          : res && typeof res === 'object' && 'slides' in (res as any) && Array.isArray((res as any).slides)
            ? ((res as any).slides as Slide[])
            : undefined
        const contentMarkdown = slidesArray
          ? slidesToMarkdown(slidesArray)
          : typeof res === 'string'
            ? res
            : JSON.stringify(res, null, 2)
        addMessage({
          id: crypto.randomUUID(),
          sessionId: sid,
          role: 'assistant',
          content: contentMarkdown,
          createdAt: Date.now(),
          status: 'sent',
          slides: slidesArray as any,
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


