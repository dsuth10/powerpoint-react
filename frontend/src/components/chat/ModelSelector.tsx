export type ModelOption = { value: string; label: string }

export type ModelSelectorProps = {
  value: string
  onChange: (value: string) => void
  options?: ModelOption[]
}

const DEFAULT_MODELS: ModelOption[] = [
  { value: 'gpt-4o', label: 'GPT‑4o' },
  { value: 'claude-3.5', label: 'Claude 3.5' },
  { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
]

export function ModelSelector({ value, onChange, options = DEFAULT_MODELS }: ModelSelectorProps) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <label htmlFor="model" className="text-gray-600 dark:text-gray-300">
        Model
      </label>
      <select
        id="model"
        className="rounded border bg-white px-2 py-1 dark:border-gray-800 dark:bg-gray-900"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  )
}

export default ModelSelector


