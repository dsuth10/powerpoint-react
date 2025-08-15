import { client } from '@/lib/api/client.gen'

// Use direct backend URL to avoid proxy issues when frontend runs locally and backend runs in Docker
const env = (import.meta as any).env || {}
const isDev = !!env?.DEV
const baseUrl: string = isDev ? 'http://localhost:8000' : (env?.VITE_API_BASE_URL || '')

console.log('API Config Debug:', { isDev, baseUrl, env: env?.DEV })

if (baseUrl) {
  console.log('Setting API base URL to:', baseUrl)
  client.setConfig({ baseUrl })
  console.log('API client config set successfully')
} else {
  console.log('No base URL set, using default configuration')
}

export {} // side-effect module


