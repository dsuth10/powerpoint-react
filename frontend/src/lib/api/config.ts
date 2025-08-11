import { client } from '@/lib/api/client.gen'

// In development, rely on Vite proxy by leaving baseUrl empty (relative URLs to /api)
// In production, allow override via VITE_API_BASE_URL
const env = (import.meta as any).env || {}
const isDev = !!env?.DEV
const baseUrl: string | undefined = isDev ? undefined : env?.VITE_API_BASE_URL

if (baseUrl) {
  client.setConfig({ baseUrl })
}

export {} // side-effect module


