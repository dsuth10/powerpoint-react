import { useDownloadsStore } from '@/stores/downloads-store'

export type DownloadManagerOptions = {
  id?: string
  filename?: string
  retry?: { attempts: number; baseMs: number; maxMs: number }
  chunkSize?: number // bytes for range requests
  signal?: AbortSignal
}

export class DownloadManager {
  static async download(url: string, opts: DownloadManagerOptions = {}) {
    const id = opts.id ?? crypto.randomUUID()
    const filenameFromHeader = (headers: Headers): string | undefined => {
      const cd = headers.get('content-disposition')
      if (!cd) return undefined
      const match = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(cd)
      return decodeURIComponent(match?.[1] ?? match?.[2] ?? '') || undefined
    }

    const store = useDownloadsStore.getState()
    store.upsert({
      id,
      url,
      filename: opts.filename,
      receivedBytes: 0,
      totalBytes: undefined,
      percent: 0,
      speedBps: 0,
      etaSeconds: undefined,
      status: 'queued',
    })

    const startTime = Date.now()
    let downloaded = 0
    let total = 0

    const attempt = async (attemptIndex: number): Promise<void> => {
      store.update(id, (d) => (d.status = 'downloading'))
      const res = await fetch(url, { signal: opts.signal })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const contentLength = res.headers.get('content-length')
      total = contentLength ? parseInt(contentLength, 10) : 0
      const filename = opts.filename ?? filenameFromHeader(res.headers)
      store.update(id, (d) => {
        d.filename = filename ?? d.filename
        d.totalBytes = total || d.totalBytes
      })

      if (!res.body) {
        const blob = await res.blob()
        downloaded = blob.size
        total = blob.size
        saveBlob(blob, filename ?? deriveFilenameFromUrl(url))
        store.update(id, (d) => {
          d.receivedBytes = downloaded
          d.totalBytes = total
          d.percent = 100
          d.speedBps = calcSpeed(startTime, downloaded)
          d.etaSeconds = 0
          d.status = 'completed'
        })
        return
      }

      const reader = res.body.getReader()
      const chunks: Uint8Array[] = []
      let lastTick = Date.now()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        if (value) {
          chunks.push(value)
          downloaded += value.byteLength
          const now = Date.now()
          if (now - lastTick > 100) {
            lastTick = now
            store.update(id, (d) => {
              d.receivedBytes = downloaded
              d.totalBytes = total || d.totalBytes
              d.percent = total ? Math.round((downloaded / total) * 100) : d.percent
              d.speedBps = calcSpeed(startTime, downloaded)
              d.etaSeconds = total && downloaded ? Math.max(0, Math.round((total - downloaded) / (d.speedBps || 1))) : d.etaSeconds
            })
          }
        }
      }
      const blob = new Blob(chunks, { type: res.headers.get('content-type') ?? 'application/octet-stream' })
      saveBlob(blob, filename ?? deriveFilenameFromUrl(url))
      store.update(id, (d) => {
        d.receivedBytes = downloaded
        d.totalBytes = total
        d.percent = 100
        d.speedBps = calcSpeed(startTime, downloaded)
        d.etaSeconds = 0
        d.status = 'completed'
      })
    }

    try {
      await attempt(0)
    } catch (err) {
      const retry = opts.retry ?? { attempts: 3, baseMs: 500, maxMs: 4000 }
      let i = 1
      while (i <= retry.attempts) {
        const delay = Math.min(retry.baseMs * 2 ** (i - 1), retry.maxMs)
        await new Promise((r) => setTimeout(r, delay))
        try {
          await attempt(i)
          return { id }
        } catch {
          i += 1
        }
      }
      store.update(id, (d) => {
        d.status = 'error'
        d.error = err instanceof Error ? err.message : 'Download error'
      })
      throw err
    }

    return { id }
  }
}

function saveBlob(blob: Blob, filename: string) {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
}

function deriveFilenameFromUrl(url: string) {
  try {
    const u = new URL(url)
    const last = u.pathname.split('/').filter(Boolean).pop()
    return last ?? 'download.bin'
  } catch {
    return 'download.bin'
  }
}

function calcSpeed(startTimeMs: number, bytes: number) {
  const dt = Math.max(1, (Date.now() - startTimeMs) / 1000)
  return Math.round(bytes / dt)
}


