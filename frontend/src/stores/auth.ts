import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export type AuthUser = {
  id: string
  name?: string
}

type AuthState = {
  isAuthenticated: boolean
  user: AuthUser | null
}

type AuthActions = {
  signIn: (user: AuthUser) => void
  signOut: () => void
}

export type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>()(
  devtools(
    immer((set) => ({
      isAuthenticated: false,
      user: null,
      signIn: (user) =>
        set((draft) => {
          draft.isAuthenticated = true
          draft.user = user
        }),
      signOut: () =>
        set((draft) => {
          draft.isAuthenticated = false
          draft.user = null
        }),
    })),
    { name: 'auth-store' },
  ),
)

export const selectIsAuthenticated = (s: AuthStore) => s.isAuthenticated
export const selectUser = (s: AuthStore) => s.user


