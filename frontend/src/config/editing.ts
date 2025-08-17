export const EDITING_CONFIG = {
  maxContentLength: 1000,
  maxBatchEdits: 10,
  supportedProviders: ['dalle', 'stability-ai', 'auto'] as const,
  defaultProvider: 'auto' as const,
  editTypes: ['title', 'bullet', 'notes', 'image'] as const,
} as const;

export type EditType = typeof EDITING_CONFIG.editTypes[number];
export type ImageProvider = typeof EDITING_CONFIG.supportedProviders[number];
