import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { useSlidesStore, selectProgress, selectIsGenerating } from '@/stores/slides-store'
import { useWebSocket } from '@/hooks/use-websocket'

export function ProgressIndicator() {
  const progress = useSlidesStore(selectProgress)
  const generating = useSlidesStore(selectIsGenerating)
  const { status, lastError, onSlideProgress, onSlideCompleted, connect } = useWebSocket()
  const [phase, setPhase] = useState('')

  useEffect(() => {
    connect()
    const off1 = onSlideProgress(({ progress }) => {
      if (progress < 30) setPhase('Parsing outline…')
      else if (progress < 60) setPhase('Generating content…')
      else if (progress < 90) setPhase('Building slides…')
      else setPhase('Finalizing…')
    })
    const off2 = onSlideCompleted(() => setPhase('Completed'))
    return () => {
      off1?.()
      off2?.()
    }
  }, [connect, onSlideCompleted, onSlideProgress])

  if (!generating && progress === 0) return null

  return (
    <div className="rounded border p-3 text-sm dark:border-gray-800">
      <div className="mb-2 flex items-center justify-between">
        <div className="font-medium">Generation Progress</div>
        <div className="text-xs text-gray-500 dark:text-gray-400">WS: {status}{lastError ? ` (${lastError})` : ''}</div>
      </div>
      <div className="relative h-2 w-full overflow-hidden rounded bg-gray-200 dark:bg-gray-800">
        <motion.div
          className="absolute left-0 top-0 h-2 bg-green-500"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ ease: 'easeOut', duration: 0.3 }}
        />
      </div>
      <div className="mt-2 text-xs text-gray-600 dark:text-gray-300">{phase} ({progress}%)</div>
    </div>
  )
}

export default ProgressIndicator


