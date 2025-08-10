import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export type ChatMessageRole = 'user' | 'assistant' | 'system'

export type ChatMessage = {
  id: string
  sessionId: string
  role: ChatMessageRole
  content: string
  createdAt: number
  status?: 'pending' | 'sent' | 'error'
}

export type ChatSession = {
  id: string
  title?: string
  createdAt: number
}

type ChatState = {
  sessions: Record<string, ChatSession>
  messagesBySession: Record<string, ChatMessage[]>
  currentSessionId: string | null
}

type ChatActions = {
  startSession: (sessionId?: string) => string
  continueSession: (sessionId: string) => void
  addMessage: (msg: ChatMessage) => void
  updateMessage: (sessionId: string, id: string, updater: (m: ChatMessage) => void) => void
  removeMessage: (sessionId: string, id: string) => void
}

export type ChatStore = ChatState & ChatActions

export const useChatStore = create<ChatStore>()(
  devtools(
    immer((set, get) => ({
      sessions: {},
      messagesBySession: {},
      currentSessionId: null,
      startSession: (sessionId) => {
        const id = sessionId ?? Math.random().toString(36).slice(2, 10)
        set((draft) => {
          if (!draft.sessions[id]) {
            draft.sessions[id] = { id, createdAt: Date.now() }
            draft.messagesBySession[id] = []
          }
          draft.currentSessionId = id
        })
        return id
      },
      continueSession: (sessionId) => {
        set((draft) => {
          if (!draft.sessions[sessionId]) {
            draft.sessions[sessionId] = { id: sessionId, createdAt: Date.now() }
            draft.messagesBySession[sessionId] = []
          }
          draft.currentSessionId = sessionId
        })
      },
      addMessage: (msg) =>
        set((draft) => {
          const arr = draft.messagesBySession[msg.sessionId] ?? []
          if (!draft.messagesBySession[msg.sessionId]) {
            draft.messagesBySession[msg.sessionId] = arr
          }
          draft.messagesBySession[msg.sessionId].push(msg)
        }),
      updateMessage: (sessionId, id, updater) =>
        set((draft) => {
          const arr = draft.messagesBySession[sessionId]
          if (!arr) return
          const m = arr.find((mm) => mm.id === id)
          if (m) updater(m)
        }),
      removeMessage: (sessionId, id) =>
        set((draft) => {
          const arr = draft.messagesBySession[sessionId]
          if (!arr) return
          draft.messagesBySession[sessionId] = arr.filter((m) => m.id !== id)
        }),
    })),
    { name: 'chat-store' },
  ),
)

export const selectCurrentSessionId = (s: ChatStore) => s.currentSessionId
export const selectMessagesForCurrent = (s: ChatStore) =>
  s.currentSessionId ? s.messagesBySession[s.currentSessionId] ?? [] : []
export const selectMessagesBySession = (sessionId: string) => (s: ChatStore) =>
  s.messagesBySession[sessionId] ?? []


