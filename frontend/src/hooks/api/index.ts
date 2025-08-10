import { useMutation } from '@tanstack/react-query'
import type { GenerateChatOutlineApiV1ChatGeneratePostData, BuildSlidesApiV1SlidesBuildPostData } from '@/lib/api/types.gen'
import { generateChatOutlineApiV1ChatGeneratePost, buildSlidesApiV1SlidesBuildPost } from '@/lib/api/sdk.gen'

export const useGenerateChatMutation = () =>
  useMutation({
    mutationFn: (body: GenerateChatOutlineApiV1ChatGeneratePostData['body']) =>
      generateChatOutlineApiV1ChatGeneratePost({ body }),
  })

export const useBuildSlidesMutation = () =>
  useMutation({
    mutationFn: (body: BuildSlidesApiV1SlidesBuildPostData['body']) => buildSlidesApiV1SlidesBuildPost({ body }),
  })


