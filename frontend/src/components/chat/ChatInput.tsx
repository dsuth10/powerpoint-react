import { FormEvent, useEffect, useRef, useState } from 'react'

export type ChatInputProps = {
  onSubmit: (text: string) => Promise<void> | void
  maxLength?: number
  disabled?: boolean
}

export function ChatInput({ onSubmit, maxLength = 4000, disabled }: ChatInputProps) {
  const [value, setValue] = useState('')
  const [error, setError] = useState<string | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const remaining = maxLength - value.length

  const handleSubmit = async (e?: FormEvent) => {
    e?.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) {
      setError('Please enter a message')
      return
    }
    setError(null)
    await onSubmit(trimmed)
    setValue('')
  }

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(200, el.scrollHeight)}px`
  }, [value])

  return (
    <form onSubmit={handleSubmit} className="flex w-full items-end gap-2">
      <div className="flex-1">
        <label htmlFor="chat-input" className="sr-only">
          Message
        </label>
        <textarea
          id="chat-input"
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value.slice(0, maxLength))}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              void handleSubmit()
            }
          }}
          placeholder="Type your message..."
          className="h-[44px] w-full resize-none rounded border bg-white p-2 text-sm outline-none ring-blue-500 focus:ring dark:border-gray-800 dark:bg-gray-900"
          disabled={disabled}
        />
        <div className="mt-1 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>{remaining} characters left</span>
          {error && <span className="text-red-600 dark:text-red-400">{error}</span>}
        </div>
      </div>
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="inline-flex items-center rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        Send
      </button>
    </form>
  )
}

export default ChatInput


