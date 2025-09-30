import { useDownloadsStore } from '@/stores/downloads-store'

export type DownloadManagerOptions = {
  id?: string
  filename?: string
  retry?: { attempts: number; baseMs: number; maxMs: number }
  chunkSize?: number // bytes for range requests (default: 1MB)
  resumable?: boolean // enable resumable downloads with Range requests (default: true)
  signal?: AbortSignal
  headers?: HeadersInit // additional headers (e.g., Authorization)
}

type PersistedChunk = {
  index: number
  data: Uint8Array
}

type PersistedDownload = {
  id: string
  url: string
  filename?: string
  totalBytes: number
  receivedBytes: number
  chunks: PersistedChunk[]
  timestamp: number
}

export class DownloadManager {
  private static readonly DB_NAME = 'download-manager-db'
  private static readonly DB_VERSION = 1
  private static readonly STORE_NAME = 'downloads'
  private static readonly DEFAULT_CHUNK_SIZE = 1024 * 1024 // 1MB

  static async download(url: string, opts: DownloadManagerOptions = {}) {
    const id = opts.id ?? crypto.randomUUID()
    const resumable = opts.resumable ?? true

    const filenameFromHeader = (headers: Headers): string | undefined => {
      const cd = headers.get('content-disposition')
      if (!cd) return undefined
      const match = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(cd)
      return decodeURIComponent(match?.[1] ?? match?.[2] ?? '') || undefined
    }

    const store = useDownloadsStore.getState()

    // Try to resume from persisted state
    let downloaded = 0
    let total = 0
    let existingChunks: PersistedChunk[] = []

    if (resumable) {
      const persisted = await DownloadManager.getPersistedDownload(id)
      if (persisted && persisted.url === url) {
        downloaded = persisted.receivedBytes
        total = persisted.totalBytes
        existingChunks = persisted.chunks
        console.log(`[DownloadManager] Resuming download ${id} from ${downloaded}/${total} bytes`)
      }
    }

    store.upsert({
      id,
      url,
      filename: opts.filename,
      receivedBytes: downloaded,
      totalBytes: total || undefined,
      percent: total ? Math.round((downloaded / total) * 100) : 0,
      speedBps: 0,
      etaSeconds: undefined,
      status: 'queued',
    })

    const startTime = Date.now()

    const attempt = async (_attemptIndex: number): Promise<void> => {
      store.update(id, (d) => (d.status = 'downloading'))

      // Prepare headers including any custom headers (e.g., Authorization)
      const headers: Record<string, string> = { ...(opts.headers as Record<string, string> || {}) }
      
      // Add Range header if resuming
      if (resumable && downloaded > 0 && total > 0) {
        headers['Range'] = `bytes=${downloaded}-`
      }

      const res = await fetch(url, { signal: opts.signal, headers })

      // Handle both 200 (full) and 206 (partial) responses
      if (!res.ok && res.status !== 206) {
        throw new Error(`HTTP ${res.status}`)
      }

      // For 206 responses, we're resuming
      const isResume = res.status === 206

      // Parse content length
      const contentLength = res.headers.get('content-length')
      const contentRange = res.headers.get('content-range')

      if (contentRange) {
        // Parse: "bytes 1024-2047/2048"
        const match = /bytes (\d+)-(\d+)\/(\d+)/.exec(contentRange)
        if (match) {
          total = parseInt(match[3], 10)
        }
      } else if (contentLength) {
        const newTotal = parseInt(contentLength, 10)
        // If not resuming, update total
        if (!isResume) {
          total = newTotal
          downloaded = 0
          existingChunks = []
        }
      }

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
      const chunks: Uint8Array[] = [...existingChunks.map((c) => c.data)]
      let chunkIndex = existingChunks.length
      let lastTick = Date.now()
      let lastPersist = Date.now()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        if (value) {
          chunks.push(value)
          downloaded += value.byteLength

          const now = Date.now()

          // Update UI every 100ms
          if (now - lastTick > 100) {
            lastTick = now
            store.update(id, (d) => {
              d.receivedBytes = downloaded
              d.totalBytes = total || d.totalBytes
              d.percent = total ? Math.round((downloaded / total) * 100) : d.percent
              d.speedBps = calcSpeed(startTime, downloaded)
              d.etaSeconds =
                total && downloaded ? Math.max(0, Math.round((total - downloaded) / (d.speedBps || 1))) : d.etaSeconds
            })
          }

          // Persist chunks every 2 seconds if resumable
          if (resumable && now - lastPersist > 2000) {
            lastPersist = now
            const persistedChunks: PersistedChunk[] = chunks.map((data, index) => ({ index, data }))
            await DownloadManager.persistDownload({
              id,
              url,
              filename,
              totalBytes: total,
              receivedBytes: downloaded,
              chunks: persistedChunks,
              timestamp: now,
            })
          }

          chunkIndex++
        }
      }

      const blob = new Blob(chunks as BlobPart[], { type: res.headers.get('content-type') ?? 'application/octet-stream' })
      saveBlob(blob, filename ?? deriveFilenameFromUrl(url))
      store.update(id, (d) => {
        d.receivedBytes = downloaded
        d.totalBytes = total
        d.percent = 100
        d.speedBps = calcSpeed(startTime, downloaded)
        d.etaSeconds = 0
        d.status = 'completed'
      })

      // Clean up persisted data on successful completion
      if (resumable) {
        await DownloadManager.deletePersistedDownload(id)
      }
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

  // IndexedDB persistence methods
  private static async openDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DownloadManager.DB_NAME, DownloadManager.DB_VERSION)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains(DownloadManager.STORE_NAME)) {
          db.createObjectStore(DownloadManager.STORE_NAME, { keyPath: 'id' })
        }
      }
    })
  }

  private static async persistDownload(download: PersistedDownload): Promise<void> {
    try {
      const db = await DownloadManager.openDB()
      const tx = db.transaction(DownloadManager.STORE_NAME, 'readwrite')
      const store = tx.objectStore(DownloadManager.STORE_NAME)
      store.put(download)
      await new Promise<void>((resolve, reject) => {
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
      })
      db.close()
    } catch (err) {
      console.error('[DownloadManager] Failed to persist download:', err)
    }
  }

  private static async getPersistedDownload(id: string): Promise<PersistedDownload | null> {
    try {
      const db = await DownloadManager.openDB()
      const tx = db.transaction(DownloadManager.STORE_NAME, 'readonly')
      const store = tx.objectStore(DownloadManager.STORE_NAME)
      const request = store.get(id)

      const result = await new Promise<PersistedDownload | undefined>((resolve, reject) => {
        request.onsuccess = () => resolve(request.result)
        request.onerror = () => reject(request.error)
      })

      db.close()
      return result || null
    } catch (err) {
      console.error('[DownloadManager] Failed to get persisted download:', err)
      return null
    }
  }

  private static async deletePersistedDownload(id: string): Promise<void> {
    try {
      const db = await DownloadManager.openDB()
      const tx = db.transaction(DownloadManager.STORE_NAME, 'readwrite')
      const store = tx.objectStore(DownloadManager.STORE_NAME)
      store.delete(id)
      await new Promise<void>((resolve, reject) => {
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
      })
      db.close()
    } catch (err) {
      console.error('[DownloadManager] Failed to delete persisted download:', err)
    }
  }

  /**
   * Clean up old persisted downloads (older than 7 days)
   */
  static async cleanupOldDownloads(): Promise<void> {
    try {
      const db = await DownloadManager.openDB()
      const tx = db.transaction(DownloadManager.STORE_NAME, 'readwrite')
      const store = tx.objectStore(DownloadManager.STORE_NAME)
      const request = store.getAll()

      const downloads = await new Promise<PersistedDownload[]>((resolve, reject) => {
        request.onsuccess = () => resolve(request.result)
        request.onerror = () => reject(request.error)
      })

      const now = Date.now()
      const maxAge = 7 * 24 * 60 * 60 * 1000 // 7 days

      for (const download of downloads) {
        if (now - download.timestamp > maxAge) {
          store.delete(download.id)
        }
      }

      await new Promise<void>((resolve, reject) => {
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
      })

      db.close()
    } catch (err) {
      console.error('[DownloadManager] Failed to cleanup old downloads:', err)
    }
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