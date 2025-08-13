export type ModelOption = { value: string; label: string }

export type ModelSelectorProps = {
  value: string
  onChange: (value: string) => void
  options?: ModelOption[]
}

// Values must match backend allowlist in settings.OPENROUTER_ALLOWED_MODELS
// to avoid fallback/minimal outlines
const DEFAULT_MODELS: ModelOption[] = [
  { value: 'openai/gpt-4o-mini', label: 'GPT‑4o mini' },
  { value: 'openai/gpt-4o', label: 'GPT‑4o' },
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


