import React, { useState, useEffect, useCallback } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'

import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Loader2, Edit3, Undo2 } from 'lucide-react'
import { editSlideContent, previewSlideEdit } from '@/hooks/api/slides'
import { useSlidesStore, selectIsEditing, selectEditingSlideIndex, selectEditHistory } from '@/stores/slides-store'
import { EDITING_CONFIG } from '@/config/editing'
import type { SlidePlan } from '@/lib/api/types.gen'

interface EditControlsProps {
  slideIndex: number
  slide: SlidePlan
}

// Form validation schema
const editFormSchema = z.object({
  editType: z.enum(['title', 'bullet', 'notes', 'image']),
  content: z.string().min(1, 'Content is required').max(1000, 'Content too long'),
  bulletIndex: z.number().optional(),
  imagePrompt: z.string().optional(),
  provider: z.enum(['dalle', 'stability-ai', 'auto']).optional(),
})

type EditFormData = z.infer<typeof editFormSchema>

export const EditControls: React.FC<EditControlsProps> = ({ slideIndex, slide }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<SlidePlan | null>(null)
  
  const queryClient = useQueryClient()
  const { slides, startEditing, cancelEditing, applyEdit, undoLastEdit } = useSlidesStore()
  const editHistory = useSlidesStore(selectEditHistory)
  const isEditingGlobal = useSlidesStore(selectIsEditing)
  const editingSlideIndex = useSlidesStore(selectEditingSlideIndex)
  
  // Form setup with validation
  const form = useForm<EditFormData>({
    resolver: zodResolver(editFormSchema),
    defaultValues: {
      editType: 'title',
      content: '',
      provider: 'auto'
    }
  })
  
  const editType = form.watch('editType')
  
  // Edit mutation with retry and error handling
  const editMutation = useMutation({
    mutationFn: editSlideContent,
    retry: (failureCount, error) => {
      // Retry up to 3 times for network errors
      if (error.message.includes('Network') && failureCount < 3) {
        return true
      }
      return false
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    onSuccess: (response) => {
      if (response.success) {
        toast.success('Slide updated successfully')
        
        // Create edit operation for history
        const editOperation = {
          id: `edit-${Date.now()}`,
          slideIndex,
          target: response.target,
          content: response.message,
          timestamp: new Date(),
          originalSlide: slide,
          updatedSlide: response.updated_slide
        }
        
        applyEdit(editOperation)
        setIsEditing(false)
        form.reset()
        queryClient.invalidateQueries({ queryKey: ['slides'] })
      } else {
        toast.error(`Edit failed: ${response.message}`)
      }
    },
    onError: (error) => {
      if (error.message.includes('Network')) {
        toast.error('Network error. Please check your connection and try again.')
      } else {
        toast.error(`Edit failed: ${error.message}`)
      }
    }
  })
  
  // Preview mutation
  const previewMutation = useMutation({
    mutationFn: previewSlideEdit,
    onSuccess: (response) => {
      if (response.success) {
        setPreviewData(response.updated_slide)
        setShowPreview(true)
      } else {
        toast.error(`Preview failed: ${response.message}`)
      }
    },
    onError: (error) => {
      toast.error(`Preview failed: ${error.message}`)
    }
  })
  
  // Handle form submission
  const handleEdit = useCallback((data: EditFormData) => {
    const request = {
      slide_index: slideIndex,
      target: data.editType,
      content: data.content,
      bullet_index: data.editType === 'bullet' ? data.bulletIndex : undefined,
      image_prompt: data.editType === 'image' ? data.imagePrompt : undefined,
      provider: data.editType === 'image' ? data.provider : undefined
    }
    
    editMutation.mutate({ request, slides })
  }, [slideIndex, slides, editMutation])
  
  // Handle preview
  const handlePreview = useCallback((data: EditFormData) => {
    const request = {
      slide_index: slideIndex,
      target: data.editType,
      content: data.content,
      bullet_index: data.editType === 'bullet' ? data.bulletIndex : undefined,
      image_prompt: data.editType === 'image' ? data.imagePrompt : undefined,
      provider: data.editType === 'image' ? data.provider : undefined
    }
    
    previewMutation.mutate({ request, slides })
  }, [slideIndex, slides, previewMutation])
  
  // Handle dialog open
  const handleOpenEdit = useCallback(() => {
    setIsEditing(true)
    startEditing(slideIndex)
    
    // Pre-populate content based on edit type
    const currentEditType = form.getValues('editType')
    if (currentEditType === 'title') {
      form.setValue('content', slide.title)
    } else if (currentEditType === 'notes') {
      form.setValue('content', (slide.notes as string) || '')
    }
  }, [slideIndex, slide, startEditing, form])
  
  // Handle dialog close
  const handleCloseEdit = useCallback(() => {
    setIsEditing(false)
    cancelEditing()
    form.reset()
    setShowPreview(false)
    setPreviewData(null)
  }, [cancelEditing, form])
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + E to edit current slide
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault()
        if (!isEditingGlobal) {
          handleOpenEdit()
        }
      }
      
      // Ctrl/Cmd + S to save changes
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        if (isEditingGlobal && form.formState.isValid) {
          form.handleSubmit(handleEdit)()
        }
      }
      
      // Escape to cancel editing
      if (e.key === 'Escape' && (isEditingGlobal || isEditing)) {
        e.preventDefault()
        handleCloseEdit()
      }
      
      // Ctrl/Cmd + Z to undo last edit
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault()
        undoLastEdit()
      }
    }
    
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isEditingGlobal, isEditing, form, handleOpenEdit, handleEdit, handleCloseEdit, undoLastEdit])
  
  // Auto-populate content when edit type changes
  useEffect(() => {
    if (editType === 'title') {
      form.setValue('content', slide.title)
    } else if (editType === 'notes') {
      form.setValue('content', (slide.notes as string) || '')
    } else {
      form.setValue('content', '')
    }
  }, [editType, slide, form])
  
  return (
    <div className="edit-controls space-y-2">
      {/* Edit Button */}
      <Button 
        onClick={handleOpenEdit} 
        variant="outline" 
        size="sm"
        disabled={isEditingGlobal && editingSlideIndex !== slideIndex}
        className="w-full"
      >
        <Edit3 className="mr-2 h-4 w-4" />
        Edit Slide
      </Button>
      
      {/* Undo Button */}
      {editHistory.length > 0 && (
        <Button 
          onClick={undoLastEdit} 
          variant="ghost" 
          size="sm"
          className="w-full"
        >
          <Undo2 className="mr-2 h-4 w-4" />
          Undo Last Edit
        </Button>
      )}
      
      {/* Edit Dialog */}
      <Dialog open={isEditing} onOpenChange={setIsEditing}>
        <DialogContent className={EDITING_CONFIG.dialogWidth}>
          <DialogHeader>
            <DialogTitle>Edit Slide {slideIndex + 1}</DialogTitle>
            <DialogDescription>
              Use AI assistance to improve your slide content. Press Ctrl+E to open, Ctrl+S to save, or Escape to cancel.
            </DialogDescription>
          </DialogHeader>
          
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleEdit)} className="space-y-4">
              {/* Edit Type Selection */}
              <FormField
                control={form.control}
                name="editType"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Edit Type</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select edit type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {EDITING_CONFIG.editTypes.map((type) => (
                          <SelectItem key={type} value={type}>
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              {/* Title Edit */}
              {editType === 'title' && (
                <FormField
                  control={form.control}
                  name="content"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>New Title</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          placeholder="Enter new title..."
                          maxLength={EDITING_CONFIG.maxTitleLength}
                        />
                      </FormControl>
                      <div className="text-xs text-muted-foreground">
                        {field.value.length}/{EDITING_CONFIG.maxTitleLength} characters
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
              
              {/* Bullet Edit */}
              {editType === 'bullet' && (
                <>
                  <FormField
                    control={form.control}
                    name="bulletIndex"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Bullet Point</FormLabel>
                        <Select onValueChange={(value) => field.onChange(parseInt(value))} value={field.value?.toString()}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select bullet point" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {slide.bullets.map((_, i) => (
                              <SelectItem key={i} value={i.toString()}>
                                {`Bullet ${i + 1}`}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="content"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>New Content</FormLabel>
                        <FormControl>
                          <Textarea
                            {...field}
                            placeholder="Enter new bullet content..."
                            maxLength={EDITING_CONFIG.maxBulletLength}
                            rows={3}
                          />
                        </FormControl>
                        <div className="text-xs text-muted-foreground">
                          {field.value.length}/{EDITING_CONFIG.maxBulletLength} characters
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}
              
              {/* Notes Edit */}
              {editType === 'notes' && (
                <FormField
                  control={form.control}
                  name="content"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>New Notes</FormLabel>
                      <FormControl>
                        <Textarea
                          {...field}
                          placeholder="Enter new notes..."
                          maxLength={EDITING_CONFIG.maxNotesLength}
                          rows={4}
                        />
                      </FormControl>
                      <div className="text-xs text-muted-foreground">
                        {field.value.length}/{EDITING_CONFIG.maxNotesLength} characters
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
              
              {/* Image Edit */}
              {editType === 'image' && (
                <>
                  <FormField
                    control={form.control}
                    name="imagePrompt"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Image Description</FormLabel>
                        <FormControl>
                          <Textarea
                            {...field}
                            placeholder="Describe the new image you want..."
                            maxLength={EDITING_CONFIG.maxContentLength}
                            rows={3}
                          />
                        </FormControl>
                        <div className="text-xs text-muted-foreground">
                          {field.value?.length || 0}/{EDITING_CONFIG.maxContentLength} characters
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="provider"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Image Provider</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {EDITING_CONFIG.supportedProviders.map((p) => (
                              <SelectItem key={p} value={p}>
                                {p === 'auto' ? 'Auto (DALL-E Preferred)' : p.toUpperCase()}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}
              
              <DialogFooter className="flex gap-2">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleCloseEdit}
                  disabled={editMutation.isPending || previewMutation.isPending}
                >
                  Cancel
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={form.handleSubmit(handlePreview)}
                  disabled={editMutation.isPending || previewMutation.isPending || !form.formState.isValid}
                >
                  {previewMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Previewing...
                    </>
                  ) : (
                    'Preview'
                  )}
                </Button>
                <Button 
                  type="submit" 
                  disabled={editMutation.isPending || previewMutation.isPending || !form.formState.isValid}
                >
                  {editMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    'Apply Edit'
                  )}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
      
      {/* Preview Dialog */}
      {showPreview && previewData && (
        <Dialog open={showPreview} onOpenChange={setShowPreview}>
          <DialogContent className="sm:max-w-[800px]">
            <DialogHeader>
              <DialogTitle>Preview Changes</DialogTitle>
              <DialogDescription>
                Review the changes before applying them to your slide.
              </DialogDescription>
            </DialogHeader>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">Original</h4>
                <div className="border rounded-lg p-4 bg-muted/50">
                  <h3 className="font-bold">{slide.title}</h3>
                  {slide.bullets && slide.bullets.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {slide.bullets.map((bullet, i) => (
                        <li key={i} className="text-sm">• {bullet}</li>
                      ))}
                    </ul>
                  )}
                  {slide.notes && typeof slide.notes === 'string' && (
                    <p className="mt-2 text-sm text-muted-foreground">{slide.notes}</p>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Edited</h4>
                <div className="border rounded-lg p-4 bg-green-50">
                  <h3 className="font-bold">{previewData.title}</h3>
                  {previewData.bullets && previewData.bullets.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {previewData.bullets.map((bullet, i) => (
                        <li key={i} className="text-sm">• {bullet}</li>
                      ))}
                    </ul>
                  )}
                  {previewData.notes && typeof previewData.notes === 'string' && (
                    <p className="mt-2 text-sm text-muted-foreground">{previewData.notes}</p>
                  )}
                </div>
              </div>
            </div>
            
            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowPreview(false)}
              >
                Cancel
              </Button>
              <Button 
                onClick={() => {
                  form.handleSubmit(handleEdit)()
                  setShowPreview(false)
                }}
                disabled={editMutation.isPending}
              >
                {editMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Applying...
                  </>
                ) : (
                  'Apply Changes'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}
