import { useEffect } from 'react'
import { Play, Pause, RotateCcw } from 'lucide-react'
import { useSlideGenerationStore } from '@/stores/slide-generation-store'
import { useBuildSlides } from '@/hooks/api/slides'
import { createGenerationSocket } from '@/lib/slide-generation-socket'
import DownloadButton from './DownloadButton'
import RetryButton from './RetryButton'
import { useState } from 'react'

// Use the same type as SlideGenerator
export type SlideOutline = { title: string; bullets?: string[] }

interface GenerationControlsProps {
  outline: SlideOutline[]
  sessionId: string
}

export default function GenerationControls({ outline, sessionId }: GenerationControlsProps) {
  const gen = useSlideGenerationStore()
  const mutation = useBuildSlides()
  const [selectedProvider, setSelectedProvider] = useState<string>('auto')
  
  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    // Update the store with the selected provider
    useSlideGenerationStore.getState().setImageProvider(provider)
  }

  // Setup WebSocket connection for progress updates
  useEffect(() => {
    if (gen.status !== 'generating') return
    
    const socket = createGenerationSocket()
    
    const onProgress = ({ jobId, progress }: { jobId: string; progress: number }) => {
      if (jobId === gen.jobId) gen.setProgress(progress)
    }
    
    const onComplete = ({ jobId, fileUrl }: { jobId: string; fileUrl?: string }) => {
      if (jobId === gen.jobId) gen.complete(fileUrl)
    }
    
    const onError = ({ jobId, message }: { jobId: string; message: string }) => {
      if (jobId === gen.jobId) gen.fail(message)
    }
    
    socket.on('slide:progress', onProgress)
    socket.on('slide:completed', onComplete)
    socket.on('error', onError)
    
    return () => {
      socket.off('slide:progress', onProgress)
      socket.off('slide:completed', onComplete)
      socket.off('error', onError)
      socket.disconnect()
    }
  }, [gen.status, gen.jobId])

  const handleGenerate = async () => {
    try {
      // Convert outline to the expected format
      const slides = outline.map((slide) => ({
        title: slide.title,
        bullets: slide.bullets || [],
        notes: (slide as any).speaker_notes,
        image: (slide as any).image_prompt,
      }))

      const result = await mutation.mutateAsync({ 
        payload: slides, 
        sessionId
      })
      gen.start(result.job_id)
      
      // If result is immediately available, mark as complete
      if (result.result_url) {
        gen.complete(result.result_url)
        gen.setProgress(100)
      }
    } catch (error) {
      gen.fail(error instanceof Error ? error.message : 'Failed to start generation')
    }
  }

  const canGenerate = outline.length > 0 && gen.status !== 'generating' && !mutation.isPending

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">Image Provider:</label>
        <select 
          value={selectedProvider} 
          onChange={(e) => handleProviderChange(e.target.value)}
          className="w-48 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="auto">Auto (Best Available)</option>
          <option value="stability-ai">Stability AI</option>
          <option value="dalle">DALL-E</option>
        </select>
      </div>
      
      <div className="flex items-center gap-2">
        {canGenerate && (
          <button
            onClick={handleGenerate}
            className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            disabled={!canGenerate}
          >
            <Play className="w-4 h-4" />
            {mutation.isPending ? 'Initializing…' : 'Build PowerPoint'}
          </button>
        )}

        {gen.status === 'generating' && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Building... {gen.progress}%
            </span>
          </div>
        )}

        {gen.status === 'error' && (
          <RetryButton onClick={() => gen.reset()} />
        )}

        {gen.jobId && gen.status === 'completed' && <DownloadButton jobId={gen.jobId} />}
      </div>
    </div>
  )
}


