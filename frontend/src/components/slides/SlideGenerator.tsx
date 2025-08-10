import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useSlides } from '@/hooks/use-slides'
import { useWebSocket } from '@/hooks/use-websocket'
import ErrorState from '@/components/ui/ErrorState'

export type SlideOutline = { title: string; bullets?: string[] }

async function buildSlides(outline: SlideOutline[], options: { theme?: string } = {}) {
  // Adjust to your generated API client when available
  const res = await fetch('http://localhost:8000/api/v1/slides/build', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(outline.map((s) => ({ ...s, theme: options.theme }))),
  })
  if (!res.ok) throw new Error(`Build failed: ${res.status}`)
  return (await res.json()) as { job_id: string; status: string }
}

export function SlideGenerator({ outline }: { outline: SlideOutline[] }) {
  const { initGeneration, setError } = useSlides()
  const [theme, setTheme] = useState('light')
  const { status: wsStatus, connect } = useWebSocket()

  const mutation = useMutation({
    mutationKey: ['slides-build'],
    mutationFn: () => buildSlides(outline, { theme }),
    onMutate: () => {
      initGeneration()
      if (wsStatus === 'idle' || wsStatus === 'disconnected') connect()
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : 'Failed to start generation'),
  })

  const canGenerate = outline && outline.length > 0 && !mutation.isPending

  return (
    <div className="rounded border p-3 text-sm dark:border-gray-800">
      <div className="mb-2 font-medium">Generate Slides</div>
      <div className="mb-2 flex items-center gap-2">
        <label htmlFor="theme" className="text-gray-600 dark:text-gray-300">
          Theme
        </label>
        <select
          id="theme"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          className="rounded border bg-white px-2 py-1 dark:border-gray-800 dark:bg-gray-900"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
      <button
        className="inline-flex items-center rounded bg-green-600 px-3 py-2 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={!canGenerate}
        onClick={() => mutation.mutate()}
      >
        {mutation.isPending ? 'Starting…' : 'Generate'}
      </button>
      {mutation.isError && (
        <div className="mt-2">
          <ErrorState message={(mutation.error as Error)?.message} onRetry={() => mutation.mutate()} />
        </div>
      )}
    </div>
  )
}

export default SlideGenerator


