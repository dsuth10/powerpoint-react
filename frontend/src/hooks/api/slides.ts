import { useMutation } from '@tanstack/react-query'
import { buildSlidesApiV1SlidesBuildPost } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

export type BuildSlidesPayload = Array<{
  title: string
  bullets?: string[]
  notes?: string
  image?: { url: string; altText?: string; provider?: string } | string
}>

export function useBuildSlides() {
  const getAuthHeaders = useAuthStore((state) => state.getAuthHeaders)
  
  return useMutation({
    mutationKey: ['slides-build'],
    mutationFn: async ({ payload, sessionId }: { payload: BuildSlidesPayload; sessionId?: string }) => {
      const res = await buildSlidesApiV1SlidesBuildPost({ 
        body: payload,
        query: sessionId ? { sessionId } : undefined,
        headers: getAuthHeaders()
      })
      if (res.error) throw res.error
      // Normalize backend response supporting both camelCase and snake_case
      const data = res.data as unknown as Record<string, unknown>
      const jobId = (data['job_id'] ?? data['jobId']) as string
      const status = (data['status'] ?? 'completed') as string
      const resultUrl = (data['result_url'] ?? data['resultUrl']) as string | null | undefined
      return { job_id: jobId, status, result_url: resultUrl }
    },
  })
}


