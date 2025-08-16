import { useParams } from '@tanstack/react-router'
import { useChatStore } from '@/stores/chat-store'
import SlideGenerator from '@/components/slides/SlideGenerator'
import GenerationProgress from '@/components/slides/GenerationProgress'
import type { SlideOutline } from '@/lib/api/client/types.gen'

export default function SlidesPage() {
  // Get sessionId from route params - will use conditional param handling
  const params = useParams({ strict: false })
  const sessionId = params.sessionId as string | undefined
  
  // Get outline from chat store
  const outline = useChatStore((s) => {
    if (!sessionId) return []
    const messages = s.messagesBySession[sessionId] ?? []
    const lastAssistantWithSlides = [...messages]
      .reverse()
      .find((m) => m.role === 'assistant' && Array.isArray(m.slides) && m.slides.length > 0)
    return (lastAssistantWithSlides?.slides ?? []) as SlideOutline[]
  })
  
  // Get current session if no sessionId provided
  const currentSessionId = useChatStore((s) => s.currentSessionId)
  const effectiveSessionId = sessionId || currentSessionId

  if (!effectiveSessionId) {
    return (
      <div className="space-y-4">
        <div className="text-xl font-semibold">Slides</div>
        <div className="text-sm text-muted-foreground">
          No active session. Start a chat to generate slides.
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="text-xl font-semibold">Slides</div>
        <div className="text-sm text-muted-foreground">
          {sessionId ? `Session: ${sessionId.slice(0, 8)}...` : 'Generate and manage your presentation files'}
        </div>
      </div>
      
      {outline.length > 0 ? (
        <div className="space-y-6">
          <SlideGenerator outline={outline} sessionId={effectiveSessionId} />
          <GenerationProgress />
        </div>
      ) : (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <div className="mx-auto max-w-md space-y-2">
            <div className="text-lg font-medium">No slides generated yet</div>
            <div className="text-sm text-muted-foreground">
              Go to the Chat section to generate a slide outline first, then come back here to create your PowerPoint file.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


