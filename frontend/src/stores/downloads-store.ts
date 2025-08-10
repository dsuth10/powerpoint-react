import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export type DownloadStatus = 'queued' | 'downloading' | 'paused' | 'completed' | 'error'

export type DownloadItem = {
  id: string
  url: string
  filename?: string
  receivedBytes: number
  totalBytes?: number
  percent: number
  speedBps: number
  etaSeconds?: number
  status: DownloadStatus
  error?: string
}

type DownloadsState = {
  items: Record<string, DownloadItem>
}

type DownloadsActions = {
  upsert: (item: DownloadItem) => void
  update: (id: string, updater: (d: DownloadItem) => void) => void
  remove: (id: string) => void
}

export type DownloadsStore = DownloadsState & DownloadsActions

export const useDownloadsStore = create<DownloadsStore>()(
  devtools(
    immer((set) => ({
      items: {},
      upsert: (item) =>
        set((draft) => {
          draft.items[item.id] = item
        }),
      update: (id, updater) =>
        set((draft) => {
          const it = draft.items[id]
          if (it) updater(it)
        }),
      remove: (id) =>
        set((draft) => {
          delete draft.items[id]
        }),
    })),
    { name: 'downloads-store' },
  ),
)

export const selectDownloads = (s: DownloadsStore) => Object.values(s.items)
export const selectDownloadById = (id: string) => (s: DownloadsStore) => s.items[id]


