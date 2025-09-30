import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { Loader2, Layers } from 'lucide-react'
import { editMultipleSlides } from '@/hooks/api/slides'
import { useSlidesStore } from '@/stores/slides-store'
import type { SlidePlan } from '@/lib/api/types.gen'

interface BatchEditControlsProps {
  slides: SlidePlan[]
}

type BatchOperation = 'add-notes' | 'improve-titles' | 'regenerate-images' | 'custom'

export const BatchEditControls: React.FC<BatchEditControlsProps> = ({ slides }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedSlides, setSelectedSlides] = useState<number[]>([])
  const [batchOperation, setBatchOperation] = useState<BatchOperation | null>(null)
  const [customContent, setCustomContent] = useState('')
  
  const { updateSlide } = useSlidesStore()
  
  const batchEditMutation = useMutation({
    mutationFn: editMultipleSlides,
    onSuccess: (response) => {
      if (response.success) {
        toast.success(`Updated ${response.results.length} slides`)
        
        // Update slides in store
        response.results.forEach((result) => {
          if (result.success) {
            updateSlide(result.slide_index, result.updated_slide)
          }
        })
        
        // Show errors if any
        if (response.errors.length > 0) {
          toast.error(`Some edits failed: ${response.errors.join(', ')}`)
        }
        
        setIsOpen(false)
        setSelectedSlides([])
        setBatchOperation(null)
        setCustomContent('')
      } else {
        toast.error(`Batch edit failed: ${response.errors.join(', ')}`)
      }
    },
    onError: (error) => {
      toast.error(`Batch edit failed: ${error.message}`)
    }
  })
  
  const handleSlideToggle = (slideIndex: number) => {
    setSelectedSlides(prev => 
      prev.includes(slideIndex) 
        ? prev.filter(i => i !== slideIndex)
        : [...prev, slideIndex]
    )
  }
  
  const handleSelectAll = () => {
    setSelectedSlides(slides.map((_, index) => index))
  }
  
  const handleDeselectAll = () => {
    setSelectedSlides([])
  }
  
  const handleBatchEdit = () => {
    if (!batchOperation || selectedSlides.length === 0) return
    
    const edits = selectedSlides.map(slideIndex => {
      const baseEdit = {
        slide_index: slideIndex,
        content: customContent || getDefaultContent(batchOperation),
      }
      
      switch (batchOperation) {
        case 'add-notes':
          return { ...baseEdit, target: 'notes' as const }
        case 'improve-titles':
          return { ...baseEdit, target: 'title' as const }
        case 'regenerate-images':
          return { 
            ...baseEdit, 
            target: 'image' as const,
            image_prompt: customContent || 'Generate a relevant image for this slide',
            provider: 'auto'
          }
        case 'custom':
          return { ...baseEdit, target: 'title' as const } // Default to title for custom
        default:
          return { ...baseEdit, target: 'title' as const }
      }
    })
    
    batchEditMutation.mutate({ 
      request: { edits }, 
      slides 
    })
  }
  
  const getDefaultContent = (operation: BatchOperation): string => {
    switch (operation) {
      case 'add-notes':
        return 'Add comprehensive speaker notes for this slide'
      case 'improve-titles':
        return 'Improve the title to be more engaging and descriptive'
      case 'regenerate-images':
        return 'Generate a relevant image for this slide'
      case 'custom':
        return customContent
      default:
        return ''
    }
  }
  
  const getOperationDescription = (operation: BatchOperation): string => {
    switch (operation) {
      case 'add-notes':
        return 'Add comprehensive speaker notes to all selected slides'
      case 'improve-titles':
        return 'Improve titles to be more engaging and descriptive'
      case 'regenerate-images':
        return 'Generate new images for all selected slides'
      case 'custom':
        return 'Apply custom content to all selected slides'
      default:
        return ''
    }
  }
  
  return (
    <div className="batch-edit-controls">
      <Button 
        onClick={() => setIsOpen(true)} 
        variant="outline" 
        size="sm"
        className="w-full"
      >
        <Layers className="mr-2 h-4 w-4" />
        Batch Edit
      </Button>
      
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Batch Edit Slides</DialogTitle>
            <DialogDescription>
              Select multiple slides and apply the same edit operation to all of them.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Slide Selection */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Select Slides ({selectedSlides.length} selected)</Label>
                <div className="space-x-2">
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="sm" 
                    onClick={handleSelectAll}
                  >
                    Select All
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="sm" 
                    onClick={handleDeselectAll}
                  >
                    Deselect All
                  </Button>
                </div>
              </div>
              
              <div className="max-h-40 overflow-y-auto border rounded-lg p-2 space-y-2">
                {slides.map((slide, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Checkbox
                      id={`slide-${index}`}
                      checked={selectedSlides.includes(index)}
                      onCheckedChange={() => handleSlideToggle(index)}
                    />
                    <Label 
                      htmlFor={`slide-${index}`} 
                      className="text-sm cursor-pointer flex-1"
                    >
                      Slide {index + 1}: {slide.title}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Operation Selection */}
            <div>
              <Label htmlFor="batch-operation">Batch Operation</Label>
              <Select value={batchOperation || ''} onValueChange={(value: BatchOperation) => setBatchOperation(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose batch operation" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="add-notes">Add notes to all</SelectItem>
                  <SelectItem value="improve-titles">Improve titles</SelectItem>
                  <SelectItem value="regenerate-images">Regenerate images</SelectItem>
                  <SelectItem value="custom">Custom operation</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Custom Content */}
            {batchOperation && (
              <div>
                <Label htmlFor="custom-content">
                  {batchOperation === 'custom' ? 'Custom Content' : 'Additional Instructions'}
                </Label>
                <Textarea
                  id="custom-content"
                  value={customContent}
                  onChange={(e) => setCustomContent(e.target.value)}
                  placeholder={getDefaultContent(batchOperation)}
                  rows={3}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  {getOperationDescription(batchOperation)}
                </p>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => setIsOpen(false)}
              disabled={batchEditMutation.isPending}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleBatchEdit}
              disabled={!batchOperation || selectedSlides.length === 0 || batchEditMutation.isPending}
            >
              {batchEditMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Applying to {selectedSlides.length} slides...
                </>
              ) : (
                `Apply to ${selectedSlides.length} Selected`
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}




