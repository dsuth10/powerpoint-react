import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { EditControls } from './EditControls'
import { useSlidesStore } from '@/stores/slides-store'
import type { SlidePlan } from '@/lib/api/types.gen'

const mockSlide: SlidePlan = {
  title: "Test Slide",
  bullets: ["Bullet 1", "Bullet 2"],
  notes: "Test notes"
}

const mockSlides = [mockSlide]

// Mock the API hook
jest.mock('@/hooks/api/slides', () => ({
  editSlideContent: jest.fn()
}))

// Mock the slides store
jest.mock('@/stores/slides-store', () => ({
  useSlidesStore: jest.fn()
}))

const mockUseSlidesStore = useSlidesStore as jest.MockedFunction<typeof useSlidesStore>

describe('EditControls', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    })

    mockUseSlidesStore.mockReturnValue({
      slides: mockSlides,
      updateSlide: jest.fn(),
      currentIndex: 0,
      generating: false,
      progress: 0,
      initGeneration: jest.fn(),
      updateProgress: jest.fn(),
      setSlides: jest.fn(),
      setError: jest.fn(),
      next: jest.fn(),
      prev: jest.fn(),
      updateSlideById: jest.fn()
    })
  })

  const renderWithQueryClient = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    )
  }

  it('renders edit button', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    expect(screen.getByText('Edit Slide')).toBeInTheDocument()
  })

  it('opens edit modal when button is clicked', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    expect(screen.getByText('Edit Slide 1')).toBeInTheDocument()
    expect(screen.getByText('Title')).toBeInTheDocument()
  })

  it('allows editing title', async () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    fireEvent.click(screen.getByText('Apply Edit'))
    
    await waitFor(() => {
      expect(screen.queryByText('Edit Slide 1')).not.toBeInTheDocument()
    })
  })

  it('allows editing bullet points', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    // Change edit type to bullet
    const editTypeSelect = screen.getByDisplayValue('Title')
    fireEvent.click(editTypeSelect)
    fireEvent.click(screen.getByText('Bullet'))
    
    // Select bullet point
    const bulletSelect = screen.getByDisplayValue('Select bullet point')
    fireEvent.click(bulletSelect)
    fireEvent.click(screen.getByText('Bullet 1'))
    
    // Enter new content
    const contentInput = screen.getByPlaceholderText('Enter new bullet content...')
    fireEvent.change(contentInput, { target: { value: 'New bullet content' } })
    
    expect(contentInput).toHaveValue('New bullet content')
  })

  it('allows editing notes', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    // Change edit type to notes
    const editTypeSelect = screen.getByDisplayValue('Title')
    fireEvent.click(editTypeSelect)
    fireEvent.click(screen.getByText('Notes'))
    
    // Enter new notes
    const notesInput = screen.getByPlaceholderText('Enter new notes...')
    fireEvent.change(notesInput, { target: { value: 'New notes content' } })
    
    expect(notesInput).toHaveValue('New notes content')
  })

  it('allows editing images', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    // Change edit type to image
    const editTypeSelect = screen.getByDisplayValue('Title')
    fireEvent.click(editTypeSelect)
    fireEvent.click(screen.getByText('Image'))
    
    // Enter image prompt
    const promptInput = screen.getByPlaceholderText('Describe the new image you want...')
    fireEvent.change(promptInput, { target: { value: 'A professional business meeting' } })
    
    // Select provider
    const providerSelect = screen.getByDisplayValue('Auto (DALL-E Preferred)')
    fireEvent.click(providerSelect)
    fireEvent.click(screen.getByText('DALLE'))
    
    expect(promptInput).toHaveValue('A professional business meeting')
  })

  it('disables apply button when content is empty', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const applyButton = screen.getByText('Apply Edit')
    expect(applyButton).toBeDisabled()
  })

  it('enables apply button when content is provided', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    fireEvent.change(titleInput, { target: { value: 'New Title' } })
    
    const applyButton = screen.getByText('Apply Edit')
    expect(applyButton).not.toBeDisabled()
  })

  it('closes modal when cancel is clicked', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    expect(screen.getByText('Edit Slide 1')).toBeInTheDocument()
    
    fireEvent.click(screen.getByText('Cancel'))
    
    expect(screen.queryByText('Edit Slide 1')).not.toBeInTheDocument()
  })

  it('pre-populates content for title edit', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    const titleInput = screen.getByPlaceholderText('Enter new title...')
    expect(titleInput).toHaveValue('Test Slide')
  })

  it('pre-populates content for notes edit', () => {
    renderWithQueryClient(<EditControls slideIndex={0} slide={mockSlide} />)
    
    fireEvent.click(screen.getByText('Edit Slide'))
    
    // Change edit type to notes
    const editTypeSelect = screen.getByDisplayValue('Title')
    fireEvent.click(editTypeSelect)
    fireEvent.click(screen.getByText('Notes'))
    
    const notesInput = screen.getByPlaceholderText('Enter new notes...')
    expect(notesInput).toHaveValue('Test notes')
  })
})
