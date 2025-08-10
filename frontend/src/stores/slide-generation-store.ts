import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export type GenerationStatus = 'idle' | 'generating' | 'completed' | 'error'

type State = {
  status: GenerationStatus
  jobId?: string
  progress: number
  error?: string
  resultUrl?: string
  downloading: boolean
}

type Actions = {
  start: (jobId: string) => void
  setProgress: (value: number) => void
  complete: (resultUrl?: string) => void
  fail: (message: string) => void
  reset: () => void
  setDownloading: (downloading: boolean) => void
}

export type SlideGenerationStore = State & Actions

export const useSlideGenerationStore = create<SlideGenerationStore>()(
  devtools(
    immer((set) => ({
      status: 'idle',
      jobId: undefined,
      progress: 0,
      error: undefined,
      resultUrl: undefined,
      downloading: false,
      start: (jobId) =>
        set((d) => {
          d.status = 'generating'
          d.jobId = jobId
          d.progress = 0
          d.error = undefined
          d.resultUrl = undefined
        }),
      setProgress: (value) =>
        set((d) => {
          d.progress = Math.max(0, Math.min(100, value))
        }),
      complete: (resultUrl) =>
        set((d) => {
          d.status = 'completed'
          d.resultUrl = resultUrl
          d.progress = 100
        }),
      fail: (message) =>
        set((d) => {
          d.status = 'error'
          d.error = message
        }),
      reset: () =>
        set((d) => {
          d.status = 'idle'
          d.jobId = undefined
          d.progress = 0
          d.error = undefined
          d.resultUrl = undefined
          d.downloading = false
        }),
      setDownloading: (downloading) =>
        set((d) => {
          d.downloading = downloading
        }),
    })),
    { name: 'slide-generation-store' },
  ),
)

export const selectGeneration = (s: SlideGenerationStore) => s


