import { io, Socket } from 'socket.io-client'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useAuthStore, selectUser } from '@/stores/auth'
import { useSlidesStore } from '@/stores/slides-store'

// Typed event payloads
export type SlideProgressEvent = { jobId: string; progress: number }
export type SlideCompletedEvent = { jobId: string; fileUrl: string }

type ServerToClientEvents = {
  'slide:progress': (payload: SlideProgressEvent) => void
  'slide:completed': (payload: SlideCompletedEvent) => void
}

type ClientToServerEvents = {
  // Extend as needed for emit events
}

export type ConnectionStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

type UseWebSocketOptions = {
  url?: string // default from env or location
  token?: string
  autoConnect?: boolean
}

export function useWebSocket(options?: UseWebSocketOptions) {
  const url = options?.url ?? `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8000/ws`
  const authUser = useAuthStore(selectUser)
  const slidesStore = useSlidesStore.getState()

  const socketRef = useRef<Socket<ServerToClientEvents, ClientToServerEvents> | null>(null)
  const [status, setStatus] = useState<ConnectionStatus>('idle')
  const [lastError, setLastError] = useState<string | null>(null)

  const connect = useCallback(
    (overrideToken?: string, sessionId?: string) => {
      if (socketRef.current) return
      setStatus('connecting')
      const token = overrideToken ?? options?.token
      const socket = io(window.location.origin, {
        path: '/ws/socket.io',
        transports: ['websocket'],
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: Infinity,
        reconnectionDelay: 500,
        reconnectionDelayMax: 5000,
        auth: sessionId ? { sessionId } : token ? { token } : authUser ? { userId: authUser.id } : undefined,
      }) as Socket<ServerToClientEvents, ClientToServerEvents>

      socketRef.current = socket

      socket.on('connect', () => {
        setStatus('connected')
        setLastError(null)
      })
      socket.on('disconnect', () => {
        setStatus('disconnected')
      })
      socket.on('connect_error', (err) => {
        setStatus('error')
        setLastError(err?.message ?? 'connect_error')
      })

      // Typed listeners
      socket.on('slide:progress', ({ progress }) => {
        slidesStore.updateProgress(progress)
      })
      socket.on('slide:completed', ({ fileUrl }) => {
        slidesStore.setSlides([])
        slidesStore.updateProgress(100)
        // Could store fileUrl in a separate store or trigger a toast
      })
    },
    [authUser, options?.token, url, slidesStore],
  )

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect()
      socketRef.current = null
      setStatus('disconnected')
    }
  }, [])

  // Allow token refresh by reconnecting with a new token
  const updateToken = useCallback(
    (newToken: string) => {
      disconnect()
      connect(newToken)
    },
    [connect, disconnect],
  )

  useEffect(() => {
    if (options?.autoConnect) connect()
    return () => {
      disconnect()
    }
  }, [connect, disconnect, options?.autoConnect])

  // Typed on helpers for external consumers
  const onSlideProgress = useCallback(
    (handler: (e: SlideProgressEvent) => void) => {
      socketRef.current?.on('slide:progress', handler)
      return () => socketRef.current?.off('slide:progress', handler)
    },
    [],
  )

  const onSlideCompleted = useCallback(
    (handler: (e: SlideCompletedEvent) => void) => {
      socketRef.current?.on('slide:completed', handler)
      return () => socketRef.current?.off('slide:completed', handler)
    },
    [],
  )

  return {
    status,
    lastError,
    connect,
    disconnect,
    updateToken,
    onSlideProgress,
    onSlideCompleted,
  }
}


