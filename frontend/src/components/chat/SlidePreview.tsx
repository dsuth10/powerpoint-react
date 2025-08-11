import type { SlidePlan } from '@/lib/api'

export type SlidePreviewProps = {
  slides: SlidePlan[]
}

export function SlidePreview({ slides }: SlidePreviewProps) {
  return (
    <div className="grid grid-cols-1 gap-3">
      {slides.map((s, i) => (
        <div key={i} className="rounded-lg border p-3 dark:border-gray-800">
          <div className="mb-2 text-sm font-semibold">Slide {i + 1}: {s.title}</div>
          {typeof s.image === 'object' && s.image && 'url' in s.image && s.image.url ? (
            <img src={String(s.image.url)} alt={String('altText' in s.image ? (s.image as any).altText ?? s.title : s.title)} className="mb-2 h-32 w-full rounded object-cover" />
          ) : null}
          {Array.isArray(s.bullets) && s.bullets.length > 0 && (
            <ul className="list-disc space-y-1 pl-5 text-sm">
              {s.bullets.map((b, bi) => (
                <li key={bi}>{b}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  )
}

export default SlidePreview


