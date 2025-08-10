import { motion } from 'framer-motion'
import { useSlideGenerationStore, selectGeneration } from '@/stores/slide-generation-store'

export function GenerationProgress() {
  const gen = useSlideGenerationStore(selectGeneration)
  if (gen.status === 'idle') return null
  return (
    <div className="rounded border p-3 text-sm dark:border-gray-800">
      <div className="mb-2 flex items-center justify-between">
        <div className="font-medium">Status: {gen.status}</div>
        {gen.error && <div className="text-red-600 dark:text-red-400">{gen.error}</div>}
      </div>
      <div className="relative h-2 w-full overflow-hidden rounded bg-gray-200 dark:bg-gray-800">
        <motion.div
          className="absolute left-0 top-0 h-2 bg-green-500"
          initial={{ width: 0 }}
          animate={{ width: `${gen.progress}%` }}
          transition={{ ease: 'easeOut', duration: 0.3 }}
        />
      </div>
      <div className="mt-2 text-xs text-gray-600 dark:text-gray-300">{gen.progress}%</div>
    </div>
  )
}

export default GenerationProgress


