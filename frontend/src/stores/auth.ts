import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import { loginApiV1AuthLoginPost } from '@/lib/api/sdk.gen'

export type AuthUser = {
  id: string
  name?: string
}

type AuthState = {
  isAuthenticated: boolean
  user: AuthUser | null
  accessToken: string | null
  refreshToken: string | null
}

type AuthActions = {
  signIn: (user: AuthUser) => void
  signOut: () => void
  login: (email: string) => Promise<void>
  setTokens: (accessToken: string, refreshToken: string) => void
  getAuthHeaders: () => Record<string, string>
}

export type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>()(
  devtools(
    immer((set, get) => ({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null,
      
      signIn: (user) =>
        set((draft) => {
          draft.isAuthenticated = true
          draft.user = user
        }),
        
      signOut: () =>
        set((draft) => {
          draft.isAuthenticated = false
          draft.user = null
          draft.accessToken = null
          draft.refreshToken = null
        }),
        
      login: async (email: string) => {
        try {
          const response = await loginApiV1AuthLoginPost({
            body: { email }
          })
          
          if (response.data) {
            set((draft) => {
              draft.isAuthenticated = true
              draft.user = { id: email, name: email }
              draft.accessToken = response.data.access_token
              draft.refreshToken = response.data.refresh_token
            })
          }
        } catch (error) {
          console.error('Login failed:', error)
          throw error
        }
      },
      
      setTokens: (accessToken: string, refreshToken: string) =>
        set((draft) => {
          draft.accessToken = accessToken
          draft.refreshToken = refreshToken
          draft.isAuthenticated = true
        }),
        
      getAuthHeaders: () => {
        const { accessToken } = get()
        return accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}
      }
    })),
    { name: 'auth-store' },
  ),
)

export const selectIsAuthenticated = (s: AuthStore) => s.isAuthenticated
export const selectUser = (s: AuthStore) => s.user
export const selectAccessToken = (s: AuthStore) => s.accessToken


