import { useMutation } from '@tanstack/react-query'
import { buildSlidesApiV1SlidesBuildPost } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import { client as apiClient } from '@/lib/api/client.gen'
import type { SlidePlan, ImageMeta } from '@/lib/api/types.gen'

// Helper function to handle API responses
const handleApiResponse = async <T>(response: any): Promise<T> => {
  if (response.error) {
    throw new Error(response.error.message || 'API request failed')
  }
  return response.data as T
}

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

export const generateSlideImages = async (
  slides: SlidePlan[],
  style?: string,
  provider?: string
): Promise<ImageMeta[]> => {
  const params = new URLSearchParams()
  if (style) params.append('style', style)
  if (provider) params.append('provider', provider)

  const response = await apiClient.post({
    url: `/api/v1/slides/generate-images?${params}`,
    body: slides,
  })
  return handleApiResponse<ImageMeta[]>(response)
}

export const buildSlides = async (
  slides: SlidePlan[],
  sessionId?: string
): Promise<{ job_id: string; status: string; message: string }> => {
  const params = new URLSearchParams()
  if (sessionId) params.append('session_id', sessionId)

  const response = await apiClient.post({
    url: `/api/v1/slides/build?${params}`,
    body: slides,
  })
  return handleApiResponse<{ job_id: string; status: string; message: string }>(response)
}

export const getJobStatus = async (jobId: string): Promise<{
  job_id: string
  status: string
  progress: number
  total: number
  message: string
  error?: string
  file_path?: string
}> => {
  const response = await apiClient.get({
    url: `/api/v1/slides/job/${jobId}`,
  })
  return handleApiResponse<{
    job_id: string
    status: string
    progress: number
    total: number
    message: string
    error?: string
    file_path?: string
  }>(response)
}

export const downloadPptx = async (jobId: string): Promise<Blob> => {
  const response = await apiClient.get({
    url: `/api/v1/slides/download/${jobId}`,
  })
  return handleApiResponse<Blob>(response)
}

// Edit API hooks
export interface EditSlideRequest {
  slide_index: number
  target: 'title' | 'bullet' | 'notes' | 'image'
  content: string
  bullet_index?: number
  image_prompt?: string
  provider?: string
}

export interface EditSlideResponse {
  success: boolean
  slide_index: number
  target: 'title' | 'bullet' | 'notes' | 'image'
  updated_slide: SlidePlan
  message: string
  image_meta?: ImageMeta
}

export interface BatchEditRequest {
  edits: EditSlideRequest[]
}

export interface BatchEditResponse {
  success: boolean
  results: EditSlideResponse[]
  errors: string[]
}

export const editSlideContent = async ({ 
  request, 
  slides 
}: { 
  request: EditSlideRequest; 
  slides: SlidePlan[] 
}): Promise<EditSlideResponse> => {
  const response = await apiClient.post({
    url: '/api/v1/slides/edit',
    body: { request, slides }
  })
  return handleApiResponse<EditSlideResponse>(response)
}

export const editMultipleSlides = async ({ 
  request, 
  slides 
}: { 
  request: BatchEditRequest; 
  slides: SlidePlan[] 
}): Promise<BatchEditResponse> => {
  const response = await apiClient.post({
    url: '/api/v1/slides/edit-batch',
    body: { request, slides }
  })
  return handleApiResponse<BatchEditResponse>(response)
}

export const previewSlideEdit = async ({ 
  request, 
  slides 
}: { 
  request: EditSlideRequest; 
  slides: SlidePlan[] 
}): Promise<EditSlideResponse> => {
  const response = await apiClient.post({
    url: '/api/v1/slides/edit-preview',
    body: { request, slides }
  })
  return handleApiResponse<EditSlideResponse>(response)
}


