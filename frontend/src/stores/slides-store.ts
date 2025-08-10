import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export type Slide = {
  id: string
  title: string
  content?: string
}

type SlidesState = {
  slides: Slide[]
  currentIndex: number
  generating: boolean
  progress: number // 0..100
  error?: string
}

type SlidesActions = {
  initGeneration: () => void
  updateProgress: (value: number) => void
  setSlides: (slides: Slide[]) => void
  setError: (msg?: string) => void
  next: () => void
  prev: () => void
  updateSlide: (id: string, updater: (s: Slide) => void) => void
}

export type SlidesStore = SlidesState & SlidesActions

export const useSlidesStore = create<SlidesStore>()(
  devtools(
    immer((set, get) => ({
      slides: [],
      currentIndex: 0,
      generating: false,
      progress: 0,
      initGeneration: () =>
        set((draft) => {
          draft.generating = true
          draft.progress = 0
          draft.error = undefined
          draft.slides = []
          draft.currentIndex = 0
        }),
      updateProgress: (value) =>
        set((draft) => {
          draft.progress = Math.max(0, Math.min(100, value))
          if (draft.progress >= 100) draft.generating = false
        }),
      setSlides: (slides) =>
        set((draft) => {
          draft.slides = slides
          draft.currentIndex = 0
          draft.generating = false
          draft.progress = 100
        }),
      setError: (msg) =>
        set((draft) => {
          draft.error = msg
          draft.generating = false
        }),
      next: () =>
        set((draft) => {
          if (draft.currentIndex < draft.slides.length - 1) draft.currentIndex += 1
        }),
      prev: () =>
        set((draft) => {
          if (draft.currentIndex > 0) draft.currentIndex -= 1
        }),
      updateSlide: (id, updater) =>
        set((draft) => {
          const s = draft.slides.find((sl) => sl.id === id)
          if (s) updater(s)
        }),
    })),
    { name: 'slides-store' },
  ),
)

export const selectCurrentSlide = (s: SlidesStore) =>
  s.slides.length ? s.slides[Math.min(s.currentIndex, s.slides.length - 1)] : undefined
export const selectProgress = (s: SlidesStore) => s.progress
export const selectIsGenerating = (s: SlidesStore) => s.generating


