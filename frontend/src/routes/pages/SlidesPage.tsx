import { useParams } from '@tanstack/react-router'
import { useChatStore } from '@/stores/chat-store'
import { useSlidesStore, selectCurrentSlide } from '@/stores/slides-store'
import SlideGenerator from '@/components/slides/SlideGenerator'
import GenerationProgress from '@/components/slides/GenerationProgress'
import { EditControls } from '@/components/slides/EditControls'
import { BatchEditControls } from '@/components/slides/BatchEditControls'
import { useEditShortcuts } from '@/hooks/use-edit-shortcuts'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-react'

// Use the same type as SlideGenerator
export type SlideOutline = { title: string; bullets?: string[] }

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

  // Get slides from store
  const { slides, currentIndex, next, prev } = useSlidesStore()
  const currentSlide = useSlidesStore(selectCurrentSlide)

  // Keyboard shortcuts
  useEditShortcuts({
    currentSlideIndex: currentIndex
  })

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
          
          {/* Slide Display and Editing */}
          {slides.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Slide Preview & Editing</h3>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={prev}
                    disabled={currentIndex === 0}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    {currentIndex + 1} of {slides.length}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={next}
                    disabled={currentIndex === slides.length - 1}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Slide Content */}
                <div className="lg:col-span-2">
                  <div className="border rounded-lg p-6 bg-white shadow-sm">
                    <h2 className="text-xl font-bold mb-4">{currentSlide?.title}</h2>
                    {currentSlide?.bullets && currentSlide.bullets.length > 0 && (
                      <ul className="space-y-2 mb-4">
                        {currentSlide.bullets.map((bullet, index) => (
                          <li key={index} className="flex items-start">
                            <span className="mr-2 mt-1">•</span>
                            <span>{bullet}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                    {currentSlide?.notes && typeof currentSlide.notes === 'string' && (
                      <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                        <h4 className="font-semibold text-sm mb-2">Speaker Notes:</h4>
                        <p className="text-sm text-muted-foreground">{currentSlide.notes}</p>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Edit Controls */}
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-3">Edit Controls</h4>
                    <div className="space-y-3">
                      {currentSlide && (
                        <EditControls 
                          slideIndex={currentIndex} 
                          slide={currentSlide}
                        />
                      )}
                    </div>
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-3">Batch Operations</h4>
                    <BatchEditControls slides={slides} />
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-3">Keyboard Shortcuts</h4>
                    <div className="text-sm space-y-1 text-muted-foreground">
                      <div>• <kbd className="px-1 py-0.5 bg-muted rounded text-xs">Ctrl+E</kbd> Edit current slide</div>
                      <div>• <kbd className="px-1 py-0.5 bg-muted rounded text-xs">Ctrl+S</kbd> Save changes</div>
                      <div>• <kbd className="px-1 py-0.5 bg-muted rounded text-xs">Escape</kbd> Cancel editing</div>
                      <div>• <kbd className="px-1 py-0.5 bg-muted rounded text-xs">Ctrl+Z</kbd> Undo last edit</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
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


