import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { EditControls } from './EditControls'
import { useSlidesStore } from '@/stores/slides-store'
import type { SlidePlan } from '@/lib/api/types.gen'

// Mock the API hooks
jest.mock('@/hooks/api/slides', () => ({
  editSlideContent: jest.fn(),
  previewSlideEdit: jest.fn(),
}))

// Mock the slides store
jest.mock('@/stores/slides-store', () => ({
  useSlidesStore: jest.fn(),
  selectIsEditing: jest.fn(),
  selectEditingSlideIndex: jest.fn(),
  selectEditHistory: jest.fn(),
}))

const mockSlide: SlidePlan = {
  title: 'Test Slide',
  bullets: ['Bullet 1', 'Bullet 2', 'Bullet 3'],
  notes: 'Test notes',
  image: 'test-image.jpg'
}

const mockSlidesStore = {
  slides: [mockSlide],
  updateSlide: jest.fn(),
  startEditing: jest.fn(),
  cancelEditing: jest.fn(),
  applyEdit: jest.fn(),
  undoLastEdit: jest.fn(),
  editHistory: []
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

describe('EditControls', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useSlidesStore as jest.Mock).mockReturnValue(mockSlidesStore)
  })

  it('renders edit button for each slide', () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    expect(screen.getByText('Edit Slide')).toBeInTheDocument()
  })

  it('opens edit dialog when button is clicked', () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    expect(screen.getByText('Edit Slide 1')).toBeInTheDocument()
  })

  it('validates form inputs before submission', async () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const submitButton = screen.getByText('Apply Edit')
    expect(submitButton).toBeDisabled()
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    expect(submitButton).not.toBeDisabled()
  })

  it('handles API errors gracefully', async () => {
    const { editSlideContent } = require('@/hooks/api/slides')
    editSlideContent.mockRejectedValue(new Error('Server error'))
    
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    fireEvent.click(screen.getByText('Apply Edit'))
    
    await waitFor(() => {
      expect(screen.getByText('Edit failed: Server error')).toBeInTheDocument()
    })
  })

  it('shows character count for title input', () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    expect(screen.getByText('10/100 characters')).toBeInTheDocument()
  })

  it('shows bullet point selection for bullet edit type', () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const editTypeSelect = screen.getByDisplayValue('Title')
    fireEvent.click(editTypeSelect)
    
    const bulletOption = screen.getByText('Bullet')
    fireEvent.click(bulletOption)
    
    expect(screen.getByText('Bullet Point')).toBeInTheDocument()
    expect(screen.getByText('Bullet 1')).toBeInTheDocument()
    expect(screen.getByText('Bullet 2')).toBeInTheDocument()
    expect(screen.getByText('Bullet 3')).toBeInTheDocument()
  })

  it('shows image provider selection for image edit type', () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const editTypeSelect = screen.getByDisplayValue('Title')
    fireEvent.click(editTypeSelect)
    
    const imageOption = screen.getByText('Image')
    fireEvent.click(imageOption)
    
    expect(screen.getByText('Image Description')).toBeInTheDocument()
    expect(screen.getByText('Image Provider')).toBeInTheDocument()
  })

  it('shows undo button when edit history exists', () => {
    const mockStoreWithHistory = {
      ...mockSlidesStore,
      editHistory: [{ id: '1', slideIndex: 0, target: 'title', content: 'test', timestamp: new Date(), originalSlide: mockSlide, updatedSlide: mockSlide }]
    }
    ;(useSlidesStore as jest.Mock).mockReturnValue(mockStoreWithHistory)
    
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    expect(screen.getByText('Undo Last Edit')).toBeInTheDocument()
  })

  it('does not show undo button when no edit history', () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    expect(screen.queryByText('Undo Last Edit')).not.toBeInTheDocument()
  })

  it('calls undoLastEdit when undo button is clicked', () => {
    const mockStoreWithHistory = {
      ...mockSlidesStore,
      editHistory: [{ id: '1', slideIndex: 0, target: 'title', content: 'test', timestamp: new Date(), originalSlide: mockSlide, updatedSlide: mockSlide }]
    }
    ;(useSlidesStore as jest.Mock).mockReturnValue(mockStoreWithHistory)
    
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Undo Last Edit'))
    
    expect(mockSlidesStore.undoLastEdit).toHaveBeenCalled()
  })

  it('shows preview dialog when preview button is clicked', async () => {
    const { previewSlideEdit } = require('@/hooks/api/slides')
    previewSlideEdit.mockResolvedValue({
      success: true,
      updated_slide: { ...mockSlide, title: 'Preview Title' }
    })
    
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    fireEvent.click(screen.getByText('Preview'))
    
    await waitFor(() => {
      expect(screen.getByText('Preview Changes')).toBeInTheDocument()
    })
  })

  it('disables buttons during loading states', async () => {
    const { editSlideContent } = require('@/hooks/api/slides')
    editSlideContent.mockImplementation(() => new Promise(() => {})) // Never resolves
    
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    fireEvent.click(screen.getByText('Apply Edit'))
    
    expect(screen.getByText('Updating...')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeDisabled()
  })

  it('resets form when dialog is closed', () => {
    renderWithProviders(<EditControls slideIndex={0} slide={mockSlide} />)
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    fireEvent.click(screen.getByText('Cancel'))
    
    // Reopen dialog
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const newTitleInput = screen.getByPlaceholderText('Enter new title...')
    expect(newTitleInput).toHaveValue('')
  })
})
