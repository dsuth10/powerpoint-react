#!/usr/bin/env node
import { createClient, defaultPlugins } from '@hey-api/openapi-ts'
import path from 'node:path'

async function main() {
  // Backend OpenAPI URL and output dir
  const input = process.env.OPENAPI_URL || path.resolve(process.cwd(), 'src/lib/api/openapi.json')
  const output = 'src/lib/api'

  await createClient({
    input,
    output,
    plugins: [
      ...defaultPlugins, // include types + sdk
      '@hey-api/client-fetch',
    ],
  })

  // Emit a small config file for base URL and headers
  console.log(`Generated client from ${input} → ${output}`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})


