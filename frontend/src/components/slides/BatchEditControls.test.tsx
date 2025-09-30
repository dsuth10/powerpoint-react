import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { BatchEditControls } from './BatchEditControls'
import { useSlidesStore } from '@/stores/slides-store'
import type { SlidePlan } from '@/lib/api/types.gen'

// Mock the API hooks
jest.mock('@/hooks/api/slides', () => ({
  editMultipleSlides: jest.fn(),
}))

// Mock the slides store
jest.mock('@/stores/slides-store', () => ({
  useSlidesStore: jest.fn(),
}))

const mockSlides: SlidePlan[] = [
  {
    title: 'Slide 1',
    bullets: ['Bullet 1', 'Bullet 2'],
    notes: 'Notes 1',
    image: 'image1.jpg'
  },
  {
    title: 'Slide 2',
    bullets: ['Bullet 3', 'Bullet 4'],
    notes: 'Notes 2',
    image: 'image2.jpg'
  },
  {
    title: 'Slide 3',
    bullets: ['Bullet 5', 'Bullet 6'],
    notes: 'Notes 3',
    image: 'image3.jpg'
  }
]

const mockSlidesStore = {
  updateSlide: jest.fn(),
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
      <Toaster />
    </QueryClientProvider>
  )
}

describe('BatchEditControls', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useSlidesStore as jest.Mock).mockReturnValue(mockSlidesStore)
  })

  it('renders batch edit button', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    expect(screen.getByText('Batch Edit')).toBeInTheDocument()
  })

  it('opens batch edit dialog when button is clicked', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    expect(screen.getByText('Batch Edit Slides')).toBeInTheDocument()
  })

  it('shows all slides in selection list', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    expect(screen.getByText('Slide 1: Slide 1')).toBeInTheDocument()
    expect(screen.getByText('Slide 2: Slide 2')).toBeInTheDocument()
    expect(screen.getByText('Slide 3: Slide 3')).toBeInTheDocument()
  })

  it('allows selecting individual slides', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    fireEvent.click(slide1Checkbox)
    
    expect(slide1Checkbox).toBeChecked()
    expect(screen.getByText('1 selected')).toBeInTheDocument()
  })

  it('allows selecting all slides', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    fireEvent.click(screen.getByText('Select All'))
    
    expect(screen.getByText('3 selected')).toBeInTheDocument()
  })

  it('allows deselecting all slides', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    fireEvent.click(screen.getByText('Select All'))
    fireEvent.click(screen.getByText('Deselect All'))
    
    expect(screen.getByText('0 selected')).toBeInTheDocument()
  })

  it('shows batch operation options', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    
    expect(screen.getByText('Add notes to all')).toBeInTheDocument()
    expect(screen.getByText('Improve titles')).toBeInTheDocument()
    expect(screen.getByText('Regenerate images')).toBeInTheDocument()
    expect(screen.getByText('Custom operation')).toBeInTheDocument()
  })

  it('shows custom content field when custom operation is selected', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Custom operation'))
    
    expect(screen.getByText('Custom Content')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('')).toBeInTheDocument()
  })

  it('shows additional instructions field for other operations', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Add notes to all'))
    
    expect(screen.getByText('Additional Instructions')).toBeInTheDocument()
  })

  it('disables apply button when no slides are selected', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    const applyButton = screen.getByText('Apply to 0 Selected')
    expect(applyButton).toBeDisabled()
  })

  it('disables apply button when no operation is selected', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select a slide but no operation
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    fireEvent.click(slide1Checkbox)
    
    const applyButton = screen.getByText('Apply to 1 Selected')
    expect(applyButton).toBeDisabled()
  })

  it('enables apply button when slides and operation are selected', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select a slide
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    fireEvent.click(slide1Checkbox)
    
    // Select an operation
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Add notes to all'))
    
    const applyButton = screen.getByText('Apply to 1 Selected')
    expect(applyButton).not.toBeDisabled()
  })

  it('calls batch edit API when apply button is clicked', async () => {
    const { editMultipleSlides } = require('@/hooks/api/slides')
    editMultipleSlides.mockResolvedValue({
      success: true,
      results: [
        { success: true, slide_index: 0, updated_slide: mockSlides[0] },
        { success: true, slide_index: 1, updated_slide: mockSlides[1] }
      ],
      errors: []
    })
    
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select slides
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    const slide2Checkbox = screen.getByLabelText('Slide 2: Slide 2')
    fireEvent.click(slide1Checkbox)
    fireEvent.click(slide2Checkbox)
    
    // Select operation
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Add notes to all'))
    
    // Apply
    fireEvent.click(screen.getByText('Apply to 2 Selected'))
    
    await waitFor(() => {
      expect(editMultipleSlides).toHaveBeenCalledWith({
        request: {
          edits: [
            {
              slide_index: 0,
              target: 'notes',
              content: 'Add comprehensive speaker notes for this slide'
            },
            {
              slide_index: 1,
              target: 'notes',
              content: 'Add comprehensive speaker notes for this slide'
            }
          ]
        },
        slides: mockSlides
      })
    })
  })

  it('shows success message when batch edit succeeds', async () => {
    const { editMultipleSlides } = require('@/hooks/api/slides')
    editMultipleSlides.mockResolvedValue({
      success: true,
      results: [
        { success: true, slide_index: 0, updated_slide: mockSlides[0] },
        { success: true, slide_index: 1, updated_slide: mockSlides[1] }
      ],
      errors: []
    })
    
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select slides and operation
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    fireEvent.click(slide1Checkbox)
    
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Add notes to all'))
    
    fireEvent.click(screen.getByText('Apply to 1 Selected'))
    
    await waitFor(() => {
      expect(screen.getByText('Updated 2 slides')).toBeInTheDocument()
    })
  })

  it('shows error message when batch edit fails', async () => {
    const { editMultipleSlides } = require('@/hooks/api/slides')
    editMultipleSlides.mockRejectedValue(new Error('API Error'))
    
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select slides and operation
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    fireEvent.click(slide1Checkbox)
    
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Add notes to all'))
    
    fireEvent.click(screen.getByText('Apply to 1 Selected'))
    
    await waitFor(() => {
      expect(screen.getByText('Batch edit failed: API Error')).toBeInTheDocument()
    })
  })

  it('shows partial success message when some edits fail', async () => {
    const { editMultipleSlides } = require('@/hooks/api/slides')
    editMultipleSlides.mockResolvedValue({
      success: true,
      results: [
        { success: true, slide_index: 0, updated_slide: mockSlides[0] },
        { success: false, slide_index: 1, error: 'Failed to update slide 2' }
      ],
      errors: ['Failed to update slide 2']
    })
    
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select slides and operation
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    const slide2Checkbox = screen.getByLabelText('Slide 2: Slide 2')
    fireEvent.click(slide1Checkbox)
    fireEvent.click(slide2Checkbox)
    
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Add notes to all'))
    
    fireEvent.click(screen.getByText('Apply to 2 Selected'))
    
    await waitFor(() => {
      expect(screen.getByText('Updated 2 slides')).toBeInTheDocument()
      expect(screen.getByText('Some edits failed: Failed to update slide 2')).toBeInTheDocument()
    })
  })

  it('shows loading state during batch edit', async () => {
    const { editMultipleSlides } = require('@/hooks/api/slides')
    editMultipleSlides.mockImplementation(() => new Promise(() => {})) // Never resolves
    
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select slides and operation
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    fireEvent.click(slide1Checkbox)
    
    const operationSelect = screen.getByDisplayValue('')
    fireEvent.click(operationSelect)
    fireEvent.click(screen.getByText('Add notes to all'))
    
    fireEvent.click(screen.getByText('Apply to 1 Selected'))
    
    expect(screen.getByText('Applying to 1 slides...')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeDisabled()
  })

  it('resets form when dialog is closed', () => {
    renderWithProviders(<BatchEditControls slides={mockSlides} />)
    fireEvent.click(screen.getByText('Batch Edit'))
    
    // Select a slide
    const slide1Checkbox = screen.getByLabelText('Slide 1: Slide 1')
    fireEvent.click(slide1Checkbox)
    
    // Close dialog
    fireEvent.click(screen.getByText('Cancel'))
    
    // Reopen dialog
    fireEvent.click(screen.getByText('Batch Edit'))
    
    expect(screen.getByText('0 selected')).toBeInTheDocument()
    expect(slide1Checkbox).not.toBeChecked()
  })
})




