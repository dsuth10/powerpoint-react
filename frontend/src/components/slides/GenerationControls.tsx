import { useEffect, useState } from 'react'
import { Play } from 'lucide-react'
import { useBuildSlides } from '@/hooks/api/slides'
import { useSlideGenerationStore } from '@/stores/slide-generation-store'
import { DownloadManager } from '@/lib/download-manager'
import { useAuthStore } from '@/stores/auth'
import RetryButton from './RetryButton'
import DownloadButton from './DownloadButton'

// Use the same type as SlideGenerator
export type SlideOutline = { title: string; bullets?: string[] }

interface GenerationControlsProps {
  outline: SlideOutline[]
  sessionId: string
}

export default function GenerationControls({ outline, sessionId }: GenerationControlsProps) {
  const mutation = useBuildSlides()
  const gen = useSlideGenerationStore()
  const [selectedProvider, setSelectedProvider] = useState<string>('dalle') // Changed from 'auto' to 'dalle'

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    // Update the store with the selected provider
    useSlideGenerationStore.getState().setImageProvider(provider)
  }

  // Real polling for job status from backend
  useEffect(() => {
    if (gen.status !== 'generating' || !gen.jobId) return

    const pollInterval = setInterval(async () => {
      try {
        // Poll the actual job status from the backend
        const response = await fetch(`http://localhost:8000/api/v1/slides/job/${gen.jobId}`, {
          headers: {
            'Authorization': `Bearer ${useAuthStore.getState().accessToken}`,
          }
        })
        
        if (response.ok) {
          const jobData = await response.json()
          const progress = jobData.progress || 0
          const total = jobData.total || 1
          const percentage = Math.round((progress / total) * 100)
          
          gen.setProgress(percentage)
          
          if (jobData.status === 'completed') {
            gen.complete()
            clearInterval(pollInterval)
            console.log('PowerPoint generation completed! Click "Download PPTX" to download.')
          } else if (jobData.status === 'failed') {
            gen.fail(jobData.error || 'PowerPoint generation failed')
            clearInterval(pollInterval)
          }
        } else {
          console.error('Failed to poll job status:', response.status)
        }
      } catch (error) {
        console.error('Error polling job status:', error)
        // Don't fail immediately, just log the error and continue polling
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(pollInterval)
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
          <option value="auto">Auto (DALL-E Preferred)</option>
          <option value="dalle">DALL-E</option>
          <option value="stability-ai">Stability AI</option>
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

        {gen.status === 'completed' && gen.jobId && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-green-600 font-medium">✅ PowerPoint ready!</span>
            <DownloadButton jobId={gen.jobId} />
          </div>
        )}
      </div>
    </div>
  )
}


