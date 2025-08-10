export function RetryButton({ onClick, disabled }: { onClick: () => void; disabled?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center rounded bg-amber-600 px-3 py-2 text-white hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-60"
    >
      Retry
    </button>
  )
}

export default RetryButton


