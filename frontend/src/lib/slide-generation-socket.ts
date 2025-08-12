import { io, Socket } from 'socket.io-client'

export type GenerationEvents = {
  'generation_started': (payload: { jobId: string }) => void
  'generation_progress': (payload: { jobId: string; progress: number }) => void
  'generation_complete': (payload: { jobId: string; fileUrl?: string }) => void
  'generation_error': (payload: { jobId: string; message: string }) => void
}

export type GenerationSocket = Socket<GenerationEvents>

export function createGenerationSocket(url?: string): GenerationSocket {
  // Socket.IO server is mounted at "/ws" with socketio_path "socket.io" on the backend
  // Connect to the HTTP origin and set the Socket.IO path accordingly
  const scheme = window.location.protocol === 'https:' ? 'https' : 'http'
  const base = url ?? `${scheme}://${window.location.hostname}:8000`
  return io(base, { path: '/ws/socket.io', transports: ['websocket'], reconnection: true }) as GenerationSocket
}


