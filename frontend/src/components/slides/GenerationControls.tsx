import { useEffect, useMemo } from 'react'
import { useBuildSlides } from '@/hooks/api/slides'
import { useSlideGenerationStore, selectGeneration } from '@/stores/slide-generation-store'
import { createGenerationSocket } from '@/lib/slide-generation-socket'
import DownloadButton from '@/components/slides/DownloadButton'
import RetryButton from '@/components/slides/RetryButton'

export function GenerationControls({ outline }: { outline: Array<{ title: string; bullets?: string[] }> }) {
  const gen = useSlideGenerationStore(selectGeneration)
  const start = useSlideGenerationStore((s) => s.start)
  const setProgress = useSlideGenerationStore((s) => s.setProgress)
  const complete = useSlideGenerationStore((s) => s.complete)
  const fail = useSlideGenerationStore((s) => s.fail)
  const reset = useSlideGenerationStore((s) => s.reset)

  const mutation = useBuildSlides()

  useEffect(() => {
    if (gen.status !== 'generating') return
    const socket = createGenerationSocket()
    const onStarted = ({ jobId }: { jobId: string }) => {
      if (jobId === gen.jobId) setProgress(1)
    }
    const onProgress = ({ jobId, progress }: { jobId: string; progress: number }) => {
      if (jobId === gen.jobId) setProgress(progress)
    }
    const onComplete = ({ jobId, fileUrl }: { jobId: string; fileUrl?: string }) => {
      if (jobId === gen.jobId) complete(fileUrl)
    }
    const onError = ({ jobId, message }: { jobId: string; message: string }) => {
      if (jobId === gen.jobId) fail(message)
    }
    socket.on('generation_started', onStarted)
    socket.on('generation_progress', onProgress)
    socket.on('generation_complete', onComplete)
    socket.on('generation_error', onError)
    return () => {
      socket.off('generation_started', onStarted)
      socket.off('generation_progress', onProgress)
      socket.off('generation_complete', onComplete)
      socket.off('generation_error', onError)
      socket.disconnect()
    }
  }, [complete, fail, gen.jobId, gen.status, setProgress])

  const canStart = outline.length > 0 && gen.status !== 'generating' && !mutation.isPending

  return (
    <div className="flex items-center gap-2">
      <button
        className="inline-flex items-center rounded bg-green-600 px-3 py-2 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={!canStart}
        onClick={async () => {
          try {
            const res = await mutation.mutateAsync(outline)
            start(res.job_id)
          } catch (e) {
            fail(e instanceof Error ? e.message : 'Failed to start generation')
          }
        }}
      >
        {mutation.isPending ? 'Starting…' : 'Start Generation'}
      </button>
      {gen.status === 'error' && <RetryButton onClick={() => reset()} />}
      {gen.status === 'completed' && gen.jobId && (
        <DownloadButton jobId={gen.jobId} />
      )}
    </div>
  )
}

export default GenerationControls


