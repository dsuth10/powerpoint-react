import { useMutation } from '@tanstack/react-query'
import { buildSlidesApiV1SlidesBuildPost } from '@/lib/api'

export type BuildSlidesPayload = Array<{ title: string; bullets?: string[] }>

export function useBuildSlides() {
  return useMutation({
    mutationKey: ['slides-build'],
    mutationFn: async (payload: BuildSlidesPayload) => {
      const res = await buildSlidesApiV1SlidesBuildPost({ body: payload })
      if (res.error) throw res.error
      // backend returns { job_id, status, result_url? }
      return res.data as unknown as { job_id: string; status: string; result_url?: string | null }
    },
  })
}


