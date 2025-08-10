export type ErrorStateProps = {
  title?: string
  message?: string
  onRetry?: () => void
}

export function ErrorState({ title = 'Something went wrong', message, onRetry }: ErrorStateProps) {
  return (
    <div role="alert" className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
      <div className="font-medium">{title}</div>
      {message && <div className="mt-1">{message}</div>}
      {onRetry && (
        <button
          className="mt-2 inline-flex rounded bg-red-600 px-3 py-1 text-white hover:bg-red-700"
          onClick={onRetry}
        >
          Retry
        </button>
      )}
    </div>
  )
}

export default ErrorState


