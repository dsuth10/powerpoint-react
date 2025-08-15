import { useMutation } from '@tanstack/react-query'
import { generateChatOutlineApiV1ChatGeneratePost } from '@/lib/api'

export type ChatGeneratePayload = {
  prompt: string
  model?: string
  slideCount: number
  language?: string
}

export function useGenerateOutline() {
  return useMutation({
    mutationKey: ['chat-generate'],
    mutationFn: async (payload: ChatGeneratePayload) => {
      const res = await generateChatOutlineApiV1ChatGeneratePost({ body: payload })
      if (res.error) throw res.error
      return res.data
    },
  })
}


