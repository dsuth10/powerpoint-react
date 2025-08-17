import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { editSlideContent } from '@/hooks/api/slides'
import { useSlidesStore } from '@/stores/slides-store'
import { EDITING_CONFIG, type EditType, type ImageProvider } from '@/config/editing'
import type { SlidePlan } from '@/lib/api/types.gen'

interface EditControlsProps {
  slideIndex: number
  slide: SlidePlan
}

export const EditControls: React.FC<EditControlsProps> = ({ slideIndex, slide }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editType, setEditType] = useState<EditType>('title')
  const [content, setContent] = useState('')
  const [bulletIndex, setBulletIndex] = useState<number | null>(null)
  const [imagePrompt, setImagePrompt] = useState('')
  const [provider, setProvider] = useState<ImageProvider>('auto')
  
  const queryClient = useQueryClient()
  const { slides, updateSlide } = useSlidesStore()
  
  const editMutation = useMutation({
    mutationFn: editSlideContent,
    onSuccess: (response) => {
      updateSlide(slideIndex, response.updated_slide)
      setIsEditing(false)
      queryClient.invalidateQueries({ queryKey: ['slides'] })
      // Reset form
      setContent('')
      setBulletIndex(null)
      setImagePrompt('')
      setProvider('auto')
    },
    onError: (error) => {
      console.error('Edit failed:', error)
      // TODO: Show error toast
    }
  })
  
  const handleEdit = () => {
    const request = {
      slide_index: slideIndex,
      target: editType,
      content,
      bullet_index: editType === 'bullet' ? bulletIndex : undefined,
      image_prompt: editType === 'image' ? imagePrompt : undefined,
      provider: editType === 'image' ? provider : undefined
    }
    
    editMutation.mutate({ request, slides })
  }
  
  const handleOpenEdit = () => {
    setIsEditing(true)
    // Pre-populate content based on edit type
    if (editType === 'title') {
      setContent(slide.title)
    } else if (editType === 'notes') {
      setContent(slide.notes || '')
    }
  }
  
  const handleCloseEdit = () => {
    setIsEditing(false)
    // Reset form
    setContent('')
    setBulletIndex(null)
    setImagePrompt('')
    setProvider('auto')
  }
  
  return (
    <div className="edit-controls">
      <Dialog open={isEditing} onOpenChange={setIsEditing}>
        <DialogTrigger asChild>
          <Button onClick={handleOpenEdit} variant="outline" size="sm">
            Edit Slide
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Slide {slideIndex + 1}</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-type">Edit Type</Label>
              <Select value={editType} onValueChange={(value: EditType) => setEditType(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {EDITING_CONFIG.editTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {editType === 'title' && (
              <div>
                <Label htmlFor="title-content">New Title</Label>
                <Input
                  id="title-content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Enter new title..."
                  maxLength={EDITING_CONFIG.maxContentLength}
                />
              </div>
            )}
            
            {editType === 'bullet' && (
              <div className="space-y-2">
                <div>
                  <Label htmlFor="bullet-index">Bullet Point</Label>
                  <Select 
                    value={bulletIndex?.toString() || ''} 
                    onValueChange={(v) => setBulletIndex(parseInt(v))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select bullet point" />
                    </SelectTrigger>
                    <SelectContent>
                      {slide.bullets.map((_, i) => (
                        <SelectItem key={i} value={i.toString()}>
                          {`Bullet ${i + 1}`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="bullet-content">New Content</Label>
                  <Textarea
                    id="bullet-content"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter new bullet content..."
                    maxLength={EDITING_CONFIG.maxContentLength}
                  />
                </div>
              </div>
            )}
            
            {editType === 'notes' && (
              <div>
                <Label htmlFor="notes-content">New Notes</Label>
                <Textarea
                  id="notes-content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Enter new notes..."
                  maxLength={EDITING_CONFIG.maxContentLength}
                  rows={4}
                />
              </div>
            )}
            
            {editType === 'image' && (
              <div className="space-y-2">
                <div>
                  <Label htmlFor="image-prompt">Image Description</Label>
                  <Textarea
                    id="image-prompt"
                    value={imagePrompt}
                    onChange={(e) => setImagePrompt(e.target.value)}
                    placeholder="Describe the new image you want..."
                    maxLength={EDITING_CONFIG.maxContentLength}
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="image-provider">Image Provider</Label>
                  <Select value={provider} onValueChange={(value: ImageProvider) => setProvider(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {EDITING_CONFIG.supportedProviders.map((p) => (
                        <SelectItem key={p} value={p}>
                          {p === 'auto' ? 'Auto (DALL-E Preferred)' : p.toUpperCase()}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button onClick={handleCloseEdit} variant="outline">
                Cancel
              </Button>
              <Button 
                onClick={handleEdit} 
                disabled={editMutation.isPending || !content.trim()}
              >
                {editMutation.isPending ? 'Editing...' : 'Apply Edit'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
