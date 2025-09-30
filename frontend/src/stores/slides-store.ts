import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import type { SlidePlan } from '@/lib/api/types.gen'

export type Slide = {
  id: string
  title: string
  content?: string
}

export type EditOperation = {
  id: string
  slideIndex: number
  target: 'title' | 'bullet' | 'notes' | 'image'
  content: string
  timestamp: Date
  originalSlide: SlidePlan
  updatedSlide: SlidePlan
}

type SlidesState = {
  slides: SlidePlan[]
  currentIndex: number
  generating: boolean
  progress: number // 0..100
  error?: string
  editing: {
    isEditing: boolean
    editingSlideIndex: number | null
    editHistory: EditOperation[]
  }
}

type SlidesActions = {
  initGeneration: () => void
  updateProgress: (value: number) => void
  setSlides: (slides: SlidePlan[]) => void
  setError: (msg?: string) => void
  next: () => void
  prev: () => void
  updateSlide: (index: number, updatedSlide: SlidePlan) => void
  updateSlideById: (id: string, updater: (s: Slide) => void) => void
  
  // Editing actions
  startEditing: (slideIndex: number) => void
  cancelEditing: () => void
  applyEdit: (editOperation: EditOperation) => void
  undoLastEdit: () => void
  updateSlideOptimistically: (slideIndex: number, updates: Partial<SlidePlan>) => void
}

export type SlidesStore = SlidesState & SlidesActions

export const useSlidesStore = create<SlidesStore>()(
  devtools(
    immer((set, get) => ({
      slides: [],
      currentIndex: 0,
      generating: false,
      progress: 0,
      editing: {
        isEditing: false,
        editingSlideIndex: null,
        editHistory: []
      },
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
      updateSlide: (index, updatedSlide) =>
        set((draft) => {
          if (index >= 0 && index < draft.slides.length) {
            draft.slides[index] = updatedSlide
          }
        }),
      updateSlideById: (id, updater) =>
        set((draft) => {
          const s = draft.slides.find((sl) => sl.title === id) // Using title as ID for now
          if (s) updater(s as any) // Type assertion for backward compatibility
        }),
      
      // Editing actions
      startEditing: (slideIndex) =>
        set((draft) => {
          draft.editing.isEditing = true
          draft.editing.editingSlideIndex = slideIndex
        }),
      cancelEditing: () =>
        set((draft) => {
          draft.editing.isEditing = false
          draft.editing.editingSlideIndex = null
        }),
      applyEdit: (editOperation) =>
        set((draft) => {
          // Update the slide
          if (editOperation.slideIndex >= 0 && editOperation.slideIndex < draft.slides.length) {
            draft.slides[editOperation.slideIndex] = editOperation.updatedSlide
          }
          
          // Add to edit history
          draft.editing.editHistory.push(editOperation)
          
          // Limit history to last 10 operations
          if (draft.editing.editHistory.length > 10) {
            draft.editing.editHistory = draft.editing.editHistory.slice(-10)
          }
          
          // Close editing mode
          draft.editing.isEditing = false
          draft.editing.editingSlideIndex = null
        }),
      undoLastEdit: () =>
        set((draft) => {
          const lastEdit = draft.editing.editHistory[draft.editing.editHistory.length - 1]
          if (lastEdit) {
            // Restore original slide
            if (lastEdit.slideIndex >= 0 && lastEdit.slideIndex < draft.slides.length) {
              draft.slides[lastEdit.slideIndex] = lastEdit.originalSlide
            }
            
            // Remove from history
            draft.editing.editHistory = draft.editing.editHistory.slice(0, -1)
          }
        }),
      updateSlideOptimistically: (slideIndex, updates) =>
        set((draft) => {
          if (slideIndex >= 0 && slideIndex < draft.slides.length) {
            draft.slides[slideIndex] = { ...draft.slides[slideIndex], ...updates }
          }
        }),
    })),
    { name: 'slides-store' },
  ),
)

export const selectCurrentSlide = (s: SlidesStore) =>
  s.slides.length ? s.slides[Math.min(s.currentIndex, s.slides.length - 1)] : undefined
export const selectProgress = (s: SlidesStore) => s.progress
export const selectIsGenerating = (s: SlidesStore) => s.generating
export const selectIsEditing = (s: SlidesStore) => s.editing.isEditing
export const selectEditingSlideIndex = (s: SlidesStore) => s.editing.editingSlideIndex
export const selectEditHistory = (s: SlidesStore) => s.editing.editHistory
export const selectSlides = (s: SlidesStore) => s.slides


