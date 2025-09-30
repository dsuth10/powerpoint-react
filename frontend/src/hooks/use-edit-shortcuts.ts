import { useEffect, useCallback } from 'react'
import { useSlidesStore, selectIsEditing, selectEditingSlideIndex } from '@/stores/slides-store'

interface UseEditShortcutsOptions {
  onEdit?: (slideIndex: number) => void
  onSave?: () => void
  onCancel?: () => void
  onUndo?: () => void
  currentSlideIndex?: number
}

export const useEditShortcuts = ({
  onEdit,
  onSave,
  onCancel,
  onUndo,
  currentSlideIndex = 0
}: UseEditShortcutsOptions = {}) => {
  const isEditing = useSlidesStore(selectIsEditing)
  const editingSlideIndex = useSlidesStore(selectEditingSlideIndex)
  
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Ctrl/Cmd + E to edit current slide
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
      e.preventDefault()
      if (!isEditing && onEdit) {
        onEdit(currentSlideIndex)
      }
    }
    
    // Ctrl/Cmd + S to save changes
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault()
      if (isEditing && onSave) {
        onSave()
      }
    }
    
    // Escape to cancel editing
    if (e.key === 'Escape' && isEditing) {
      e.preventDefault()
      if (onCancel) {
        onCancel()
      }
    }
    
    // Ctrl/Cmd + Z to undo last edit
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
      e.preventDefault()
      if (onUndo) {
        onUndo()
      }
    }
  }, [isEditing, editingSlideIndex, currentSlideIndex, onEdit, onSave, onCancel, onUndo])
  
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
  
  return {
    isEditing,
    editingSlideIndex
  }
}




