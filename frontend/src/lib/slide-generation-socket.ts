import { io, Socket } from 'socket.io-client'

export type GenerationEvents = {
  'slide:progress': (payload: { jobId: string; progress: number }) => void
  'slide:completed': (payload: { jobId: string; fileUrl?: string }) => void
  'error': (payload: { jobId: string; message: string }) => void
}

export type GenerationSocket = Socket<GenerationEvents>

export function createGenerationSocket(url?: string): GenerationSocket {
  // Socket.IO server is mounted at "/ws" with socketio_path "socket.io" on the backend
  // Connect to the current origin (which will be proxied to backend) and set the Socket.IO path accordingly
  const base = url ?? window.location.origin
  return io(base, { path: '/ws/socket.io', transports: ['websocket'], reconnection: true }) as GenerationSocket
}


