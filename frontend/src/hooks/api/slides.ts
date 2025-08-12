import { useMutation } from '@tanstack/react-query'
import { buildSlidesApiV1SlidesBuildPost } from '@/lib/api'

export type BuildSlidesPayload = Array<{ title: string; bullets?: string[] }>

export function useBuildSlides() {
  return useMutation({
    mutationKey: ['slides-build'],
    mutationFn: async (payload: BuildSlidesPayload) => {
      const res = await buildSlidesApiV1SlidesBuildPost({ body: payload })
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


