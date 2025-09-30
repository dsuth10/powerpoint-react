# Slide Editing UI Implementation Plan

**Date:** January 2025  
**Status:** Planning Phase  
**Priority:** High  
**Dependencies:** Task 31 (Slide Editing API and Services) - ✅ Complete  
**Related Documents:** [slide-editing-implementation-plan.md](slide-editing-implementation-plan.md)

## Executive Summary

This plan outlines the implementation of the frontend UI components for AI-assisted slide editing functionality. The backend infrastructure is already complete, including all API endpoints, services, and models. This plan focuses on completing the frontend implementation to provide a seamless editing experience.

## Current Implementation Status

### ✅ Backend Infrastructure (Complete)
- **API Endpoints**: `/slides/edit`, `/slides/edit-batch`, `/slides/edit-preview`
- **Services**: `TextEditingService`, `ImageEditingService`
- **Models**: `EditSlideRequest`, `EditSlideResponse`, `BatchEditRequest`
- **Configuration**: Rate limiting, validation, error handling
- **Tests**: Comprehensive backend test coverage

### ✅ Frontend Foundation (Mostly Complete)
- **API Hooks**: `editSlideContent`, `editMultipleSlides`, `previewSlideEdit`
- **Configuration**: `EDITING_CONFIG` with proper TypeScript types
- **Basic Component**: `EditControls` component with basic structure
- **Store Integration**: Zustand store hooks for state management

### 🔄 Frontend UI (Needs Completion)
- **EditControls Component**: Basic structure exists, needs completion
- **Form Validation**: Client-side validation implementation
- **Error Handling**: User-friendly error states and feedback
- **Loading States**: Proper UX during API operations
- **Accessibility**: ARIA labels and keyboard navigation

## Architecture Alignment

The implementation follows established patterns in the codebase:

- **FastAPI** with Pydantic v2 models and strict validation
- **React 18** with TypeScript and function components
- **TanStack Query v5** for API state management
- **shadcn/ui** components for consistent UI
- **Zustand v4.5** for state management
- **Zod** for schema validation
- **Tailwind CSS** for styling

## Implementation Phases

### Phase 1: Complete EditControls Component (Week 1)

#### 1.1 Enhanced Dialog UI
**Current State**: Basic dialog structure exists but needs completion

**Required Improvements**:
```typescript
// Enhanced EditControls with proper form handling
export const EditControls: React.FC<EditControlsProps> = ({ slideIndex, slide }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editType, setEditType] = useState<EditType>('title')
  
  // Form validation with Zod
  const formSchema = z.object({
    editType: z.enum(['title', 'bullet', 'notes', 'image']),
    content: z.string().min(1, 'Content is required').max(1000, 'Content too long'),
    bulletIndex: z.number().optional(),
    imagePrompt: z.string().optional(),
    provider: z.enum(['dalle', 'stability-ai', 'auto']).optional(),
  })
  
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      editType: 'title',
      content: '',
      provider: 'auto'
    }
  })
  
  // Enhanced mutation with proper error handling
  const editMutation = useMutation({
    mutationFn: editSlideContent,
    onSuccess: (response) => {
      toast.success('Slide updated successfully')
      updateSlide(slideIndex, response.updated_slide)
      setIsEditing(false)
      form.reset()
    },
    onError: (error) => {
      toast.error(`Edit failed: ${error.message}`)
    }
  })
}
```

**Key Features to Implement**:
- **Form Validation**: Real-time validation with Zod schemas
- **Loading States**: Proper loading indicators during API calls
- **Error Handling**: User-friendly error messages with retry options
- **Keyboard Navigation**: Esc to close, Enter to submit
- **Accessibility**: ARIA labels and screen reader support
- **Character Count**: Visual feedback for content length limits

#### 1.2 Form Validation Implementation
```typescript
// Client-side validation with real-time feedback
const validateContent = (content: string, editType: EditType) => {
  if (!content.trim()) {
    return 'Content is required'
  }
  
  if (content.length > EDITING_CONFIG.maxContentLength) {
    return `Content must be ${EDITING_CONFIG.maxContentLength} characters or less`
  }
  
  if (editType === 'bullet' && bulletIndex === null) {
    return 'Please select a bullet point to edit'
  }
  
  if (editType === 'image' && !imagePrompt?.trim()) {
    return 'Image prompt is required for image editing'
  }
  
  return null
}
```

#### 1.3 Enhanced User Experience
```typescript
// Loading states and user feedback
const EditDialog = () => (
  <Dialog open={isEditing} onOpenChange={setIsEditing}>
    <DialogContent className="sm:max-w-[600px]">
      <DialogHeader>
        <DialogTitle>Edit Slide {slideIndex + 1}</DialogTitle>
        <DialogDescription>
          Use AI assistance to improve your slide content
        </DialogDescription>
      </DialogHeader>
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleEdit)} className="space-y-4">
          {/* Form fields with validation */}
          
          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => setIsEditing(false)}
              disabled={editMutation.isPending}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={editMutation.isPending || !form.formState.isValid}
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
)
```

### Phase 2: Integration and State Management (Week 2)

#### 2.1 Store Integration
**Current State**: Basic store integration exists

**Required Improvements**:
```typescript
// Enhanced slides store with editing support
interface SlidesStore {
  slides: SlidePlan[]
  currentIndex: number
  generating: boolean
  progress: number
  editing: {
    isEditing: boolean
    editingSlideIndex: number | null
    editHistory: EditOperation[]
  }
  
  // Actions
  updateSlide: (index: number, slide: SlidePlan) => void
  startEditing: (slideIndex: number) => void
  cancelEditing: () => void
  applyEdit: (editOperation: EditOperation) => void
  undoLastEdit: () => void
}

// Optimistic updates for better UX
const updateSlideOptimistically = (slideIndex: number, updates: Partial<SlidePlan>) => {
  set((state) => ({
    slides: state.slides.map((slide, index) => 
      index === slideIndex ? { ...slide, ...updates } : slide
    )
  }))
}
```

#### 2.2 Route Integration
```typescript
// Ensure EditControls are properly integrated
export const SlidesPage = () => {
  const { slides, currentIndex } = useSlidesStore()
  const currentSlide = slides[currentIndex]
  
  return (
    <div className="slides-page">
      <div className="slide-content">
        {/* Slide display */}
        <SlideDisplay slide={currentSlide} />
        
        {/* Edit controls */}
        <EditControls 
          slideIndex={currentIndex} 
          slide={currentSlide}
        />
      </div>
      
      {/* Navigation controls */}
      <SlideNavigation />
    </div>
  )
}
```

### Phase 3: Advanced Features (Week 3)

#### 3.1 Batch Editing Interface
```typescript
// Multi-select interface for batch operations
const BatchEditControls = () => {
  const [selectedSlides, setSelectedSlides] = useState<number[]>([])
  const [batchOperation, setBatchOperation] = useState<BatchOperation | null>(null)
  
  const batchEditMutation = useMutation({
    mutationFn: editMultipleSlides,
    onSuccess: (response) => {
      if (response.success) {
        toast.success(`Updated ${response.results.length} slides`)
        setSelectedSlides([])
      } else {
        toast.error(`Some edits failed: ${response.errors.join(', ')}`)
      }
    }
  })
  
  return (
    <div className="batch-edit-controls">
      <div className="selection-info">
        {selectedSlides.length} slides selected
      </div>
      
      <Select value={batchOperation} onValueChange={setBatchOperation}>
        <SelectTrigger>
          <SelectValue placeholder="Choose batch operation" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="add-notes">Add notes to all</SelectItem>
          <SelectItem value="improve-titles">Improve titles</SelectItem>
          <SelectItem value="regenerate-images">Regenerate images</SelectItem>
        </SelectContent>
      </Select>
      
      <Button 
        onClick={handleBatchEdit}
        disabled={!batchOperation || selectedSlides.length === 0}
      >
        Apply to Selected
      </Button>
    </div>
  )
}
```

#### 3.2 Preview Mode
```typescript
// Real-time preview of changes
const EditPreview = ({ originalSlide, editedSlide }: EditPreviewProps) => {
  return (
    <div className="edit-preview">
      <div className="preview-header">
        <h3>Preview Changes</h3>
        <div className="preview-controls">
          <Button variant="outline" onClick={handleCancel}>
            Cancel
          </Button>
          <Button onClick={handleApply}>
            Apply Changes
          </Button>
        </div>
      </div>
      
      <div className="preview-content">
        <div className="original-slide">
          <h4>Original</h4>
          <SlideDisplay slide={originalSlide} />
        </div>
        
        <div className="edited-slide">
          <h4>Edited</h4>
          <SlideDisplay slide={editedSlide} />
        </div>
      </div>
    </div>
  )
}
```

#### 3.3 Keyboard Shortcuts
```typescript
// Global keyboard shortcuts for editing
const useEditShortcuts = () => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + E to edit current slide
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault()
        startEditing(currentIndex)
      }
      
      // Ctrl/Cmd + S to save changes
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        if (isEditing) {
          handleSave()
        }
      }
      
      // Escape to cancel editing
      if (e.key === 'Escape' && isEditing) {
        e.preventDefault()
        cancelEditing()
      }
    }
    
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isEditing, currentIndex])
}
```

### Phase 4: Testing and Polish (Week 4)

#### 4.1 Comprehensive Testing Strategy

**Unit Tests**:
```typescript
// EditControls component tests
describe('EditControls', () => {
  it('renders edit button for each slide', () => {
    render(<EditControls slideIndex={0} slide={mockSlide} />)
    expect(screen.getByText('Edit Slide')).toBeInTheDocument()
  })
  
  it('opens edit dialog when button is clicked', () => {
    render(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    expect(screen.getByText('Edit Slide 1')).toBeInTheDocument()
  })
  
  it('validates form inputs before submission', async () => {
    render(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const submitButton = screen.getByText('Apply Edit')
    expect(submitButton).toBeDisabled()
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    expect(submitButton).not.toBeDisabled()
  })
  
  it('handles API errors gracefully', async () => {
    server.use(
      rest.post('/api/v1/slides/edit', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ detail: 'Server error' }))
      })
    )
    
    render(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    fireEvent.click(screen.getByText('Apply Edit'))
    
    await waitFor(() => {
      expect(screen.getByText('Edit failed: Server error')).toBeInTheDocument()
    })
  })
})
```

**Integration Tests**:
```typescript
// End-to-end editing workflow
describe('Slide Editing Workflow', () => {
  it('completes full editing workflow', async () => {
    // Navigate to slides page
    render(<App />)
    fireEvent.click(screen.getByText('Slides'))
    
    // Open edit dialog
    fireEvent.click(screen.getByText('Edit Slide'))
    
    // Fill out form
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'Updated Title' } })
    
    // Submit edit
    fireEvent.click(screen.getByText('Apply Edit'))
    
    // Verify success
    await waitFor(() => {
      expect(screen.getByText('Slide updated successfully')).toBeInTheDocument()
    })
    
    // Verify slide was updated
    expect(screen.getByText('Updated Title')).toBeInTheDocument()
  })
})
```

#### 4.2 Performance Optimization

**Debounced API Calls**:
```typescript
// Debounced validation for real-time feedback
const useDebouncedValidation = (content: string, delay: number = 300) => {
  const [validationResult, setValidationResult] = useState<string | null>(null)
  
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      const result = validateContent(content, editType)
      setValidationResult(result)
    }, delay)
    
    return () => clearTimeout(timeoutId)
  }, [content, editType, delay])
  
  return validationResult
}
```

**Memoization**:
```typescript
// Memoized form components for performance
const EditFormFields = memo(({ editType, form }: EditFormFieldsProps) => {
  switch (editType) {
    case 'title':
      return <TitleEditField form={form} />
    case 'bullet':
      return <BulletEditField form={form} />
    case 'notes':
      return <NotesEditField form={form} />
    case 'image':
      return <ImageEditField form={form} />
    default:
      return null
  }
})
```

#### 4.3 Error Handling and Recovery

**Network Error Recovery**:
```typescript
// Retry mechanism for failed API calls
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
  onError: (error) => {
    if (error.message.includes('Network')) {
      toast.error('Network error. Retrying...')
    } else {
      toast.error(`Edit failed: ${error.message}`)
    }
  }
})
```

**Graceful Degradation**:
```typescript
// Fallback to manual editing if AI services are unavailable
const useEditMode = () => {
  const [aiAvailable, setAiAvailable] = useState(true)
  
  const checkAIServices = async () => {
    try {
      const response = await fetch('/api/v1/slides/providers')
      const data = await response.json()
      setAiAvailable(data.available.length > 0)
    } catch {
      setAiAvailable(false)
    }
  }
  
  useEffect(() => {
    checkAIServices()
  }, [])
  
  return {
    aiAvailable,
    editMode: aiAvailable ? 'ai-assisted' : 'manual'
  }
}
```

## Configuration Updates

### Frontend Configuration (`frontend/src/config/editing.ts`)
```typescript
export const EDITING_CONFIG = {
  maxContentLength: 1000,
  maxBatchEdits: 10,
  supportedProviders: ['dalle', 'stability-ai', 'auto'] as const,
  defaultProvider: 'auto' as const,
  editTypes: ['title', 'bullet', 'notes', 'image'] as const,
  
  // UI Configuration
  dialogWidth: 'sm:max-w-[600px]',
  animationDuration: 200,
  
  // Validation
  minContentLength: 1,
  maxTitleLength: 100,
  maxBulletLength: 200,
  maxNotesLength: 500,
  
  // Keyboard shortcuts
  shortcuts: {
    edit: 'Ctrl+E',
    save: 'Ctrl+S',
    cancel: 'Escape',
    preview: 'Ctrl+P'
  }
} as const
```

### Environment Variables
```bash
# Frontend environment variables (optional)
VITE_EDITING_ENABLED=true
VITE_EDITING_PREVIEW_MODE=false
VITE_EDITING_BATCH_MODE=true
```

## Success Metrics

### User Experience Metrics
- **Edit Success Rate**: >95% of edit operations complete successfully
- **Edit Time**: Average time to complete an edit <30 seconds
- **Error Recovery**: >90% of users successfully recover from errors
- **User Satisfaction**: >4.5/5 rating for editing experience

### Technical Metrics
- **API Response Time**: <2 seconds for edit operations
- **Error Rate**: <5% of edit requests fail
- **Accessibility Score**: 100% WCAG 2.1 AA compliance
- **Test Coverage**: >90% for editing-related code

## Risk Mitigation

### Technical Risks
1. **API Rate Limiting**: Implement exponential backoff and user feedback
2. **Network Failures**: Robust error handling with retry mechanisms
3. **State Synchronization**: Optimistic updates with rollback capability
4. **Performance Issues**: Memoization and debouncing for expensive operations

### User Experience Risks
1. **Complex UI**: Progressive disclosure and contextual help
2. **Slow Operations**: Loading states and progress indicators
3. **Confusing Workflows**: Clear navigation and feedback
4. **Accessibility Issues**: Comprehensive testing with screen readers

## Dependencies and Prerequisites

### Required Dependencies
- **Backend**: All slide editing endpoints must be functional
- **Frontend**: TanStack Query, React Hook Form, Zod
- **UI**: shadcn/ui Dialog, Form, Button components
- **Testing**: Vitest, React Testing Library, MSW

### Optional Dependencies
- **Toast Notifications**: react-hot-toast or similar
- **Icons**: Lucide React for loading and status icons
- **Animations**: Framer Motion for smooth transitions

## Implementation Timeline

### Week 1: Core Functionality
- Complete EditControls component
- Implement form validation
- Add basic error handling
- Create unit tests

### Week 2: Integration
- Integrate with slides store
- Add loading states
- Implement keyboard shortcuts
- Create integration tests

### Week 3: Advanced Features
- Add batch editing interface
- Implement preview mode
- Add undo/redo functionality
- Performance optimization

### Week 4: Polish and Testing
- Comprehensive testing
- Accessibility improvements
- Performance optimization
- Documentation and final review

## Conclusion

This implementation plan builds upon the solid foundation already established in the codebase. The backend infrastructure is complete and production-ready, providing all necessary APIs and services. The frontend implementation focuses on creating a seamless, accessible, and performant editing experience that aligns with the established patterns and best practices of the project.

The phased approach ensures that core functionality is delivered quickly while advanced features are developed iteratively. The emphasis on testing, accessibility, and error handling ensures a robust and user-friendly editing experience.

## Related Documents

- [slide-editing-implementation-plan.md](slide-editing-implementation-plan.md) - Backend implementation details
- [frontend-README.md](frontend-README.md) - Frontend architecture and patterns
- [module-specs.md](module-specs.md) - API specifications and contracts
- [versions.md](versions.md) - Dependency versions and compatibility
