import { useSlidesStore } from '@/stores/slides-store'

export function useSlides() {
  const initGeneration = useSlidesStore((s) => s.initGeneration)
  const updateProgress = useSlidesStore((s) => s.updateProgress)
  const setSlides = useSlidesStore((s) => s.setSlides)
  const setError = useSlidesStore((s) => s.setError)
  const next = useSlidesStore((s) => s.next)
  const prev = useSlidesStore((s) => s.prev)
  const updateSlide = useSlidesStore((s) => s.updateSlide)

  return { initGeneration, updateProgress, setSlides, setError, next, prev, updateSlide }
}


