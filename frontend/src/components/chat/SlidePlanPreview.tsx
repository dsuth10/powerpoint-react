export type SlideSection = {
  title: string
  bullets?: string[]
  sections?: SlideSection[]
}

export type SlidePlanPreviewProps = {
  plan: SlideSection[]
}

export function SlidePlanPreview({ plan }: SlidePlanPreviewProps) {
  return (
    <div className="rounded border bg-white p-3 text-sm dark:border-gray-800 dark:bg-gray-900">
      <div className="font-medium">Proposed Slide Outline</div>
      <div className="mt-2 space-y-2">
        {plan.map((s, i) => (
          <Section key={i} section={s} level={0} />
        ))}
      </div>
    </div>
  )
}

function Section({ section, level }: { section: SlideSection; level: number }) {
  return (
    <details open className={`group rounded ${level ? 'ml-2 pl-2' : ''}`}>
      <summary className="cursor-pointer select-none text-gray-800 dark:text-gray-200">
        <span className="mr-2 inline-block h-2 w-2 rounded-full bg-blue-400 group-open:bg-green-400" />
        {section.title}
      </summary>
      {section.bullets && (
        <ul className="ml-4 mt-1 list-disc space-y-1 text-gray-700 dark:text-gray-300">
          {section.bullets.map((b, i) => (
            <li key={i}>{b}</li>
          ))}
        </ul>
      )}
      {section.sections && (
        <div className="mt-1 space-y-1">
          {section.sections.map((child, i) => (
            <Section key={i} section={child} level={level + 1} />
          ))}
        </div>
      )}
    </details>
  )
}

export default SlidePlanPreview


