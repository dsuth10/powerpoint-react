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
} as const;

export type EditType = typeof EDITING_CONFIG.editTypes[number];
export type ImageProvider = typeof EDITING_CONFIG.supportedProviders[number];

// Validation schemas
export const editFormSchema = {
  editType: 'title' as const,
  content: '',
  bulletIndex: undefined as number | undefined,
  imagePrompt: '',
  provider: 'auto' as ImageProvider,
} as const;
