import { useState } from 'react'
import ErrorState from '@/components/ui/ErrorState'
import { DownloadManager } from '@/lib/download-manager'

export function DownloadButton({ jobId, disabled }: { jobId: string; disabled?: boolean }) {
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const onClick = async () => {
    try {
      setLoading(true)
      const url = new URL(`http://localhost:8000/api/v1/slides/download/${jobId}`)
      await DownloadManager.download(url.toString(), {
        filename: `presentation-${jobId}.pptx`,
        retry: { attempts: 3, baseMs: 500, maxMs: 4000 },
      })
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Download failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <button
        onClick={onClick}
        disabled={disabled || loading}
        className="inline-flex items-center rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Downloading…' : 'Download PPTX'}
      </button>
      {error && (
        <div className="mt-2">
          <ErrorState message={error} onRetry={onClick} />
        </div>
      )}
    </div>
  )
}

export default DownloadButton


