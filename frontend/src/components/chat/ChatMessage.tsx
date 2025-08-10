import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'

export type ChatMessageProps = {
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt?: number
  model?: string
  pending?: boolean
}

export function ChatMessage({ role, content, createdAt, model, pending }: ChatMessageProps) {
  const isUser = role === 'user'
  const isAssistant = role === 'assistant'

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18 }}
      className={`rounded-lg border p-3 text-sm ${
        isUser
          ? 'border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950'
          : isAssistant
            ? 'border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900'
            : 'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950'
      }`}
    >
      {pending ? (
        <div className="animate-pulse space-y-2">
          <div className="h-3 w-1/2 rounded bg-gray-300/60 dark:bg-gray-700" />
          <div className="h-3 w-5/6 rounded bg-gray-300/60 dark:bg-gray-700" />
          <div className="h-3 w-2/3 rounded bg-gray-300/60 dark:bg-gray-700" />
        </div>
      ) : (
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
      <div className="mt-2 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>{createdAt ? new Date(createdAt).toLocaleTimeString() : ''}</span>
        {model && <span>Model: {model}</span>}
      </div>
    </motion.div>
  )
}

export default ChatMessage


