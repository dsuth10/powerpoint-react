import { useEffect, useState } from 'react'

export type ToastKind = 'success' | 'error' | 'info'

export function Toast({ kind = 'info', message, onClose }: { kind?: ToastKind; message: string; onClose?: () => void }) {
  const [open, setOpen] = useState(true)
  useEffect(() => {
    const t = setTimeout(() => {
      setOpen(false)
      onClose?.()
    }, 3500)
    return () => clearTimeout(t)
  }, [onClose])
  if (!open) return null
  const base = 'fixed bottom-4 right-4 z-50 rounded px-4 py-3 text-sm shadow-lg'
  const cls =
    kind === 'success'
      ? `${base} bg-green-600 text-white`
      : kind === 'error'
        ? `${base} bg-red-600 text-white`
        : `${base} bg-gray-900 text-white`
  return <div className={cls} role="status">{message}</div>
}

export default Toast


