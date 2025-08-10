import { io, Socket } from 'socket.io-client'

export type GenerationEvents = {
  'generation_started': (payload: { jobId: string }) => void
  'generation_progress': (payload: { jobId: string; progress: number }) => void
  'generation_complete': (payload: { jobId: string; fileUrl?: string }) => void
  'generation_error': (payload: { jobId: string; message: string }) => void
}

export type GenerationSocket = Socket<GenerationEvents>

export function createGenerationSocket(url?: string): GenerationSocket {
  const base = url ?? `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8000/ws`
  return io(base, { path: '/ws', transports: ['websocket'], reconnection: true }) as GenerationSocket
}


