import { createRouter } from '@tanstack/react-router'
import rootRoute from './routes/__root.route'
import indexRoute from './routes/index.route'
import chatIndexRoute, { chatSessionRoute } from './routes/chat/index.route'
import slidesIndexRoute from './routes/slides/index.route'
import { slidesSessionRoute } from './routes/slides/index.route'
import slideIdRoute from './routes/slides/$slideId.route'

// Manually compose routes without the vite plugin
const routeTree = rootRoute.addChildren([
  indexRoute,
  chatIndexRoute.addChildren([chatSessionRoute]),
  slidesIndexRoute.addChildren([slidesSessionRoute, slideIdRoute]),
])

console.log('Route tree:', routeTree)

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
  // v1 router option is defaultNotFoundComponent in latest; for 1.15 fallback to defaultComponent
  // @ts-expect-error Compat for older router types
  defaultNotFoundComponent: () => 'Page not found',
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
} 