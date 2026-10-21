import { Fragment, type ReactNode } from 'react'

/** Render "*highlight*" segments with the given tag (em by default) — the admin's tiny markup. */
export function rich(text: string, Tag: 'em' | 'span' = 'em'): ReactNode {
  const parts = (text ?? '').split(/(\*[^*]+\*)/g)
  return parts.map((part, i) =>
    part.startsWith('*') && part.endsWith('*') && part.length > 2
      ? <Tag key={i}>{part.slice(1, -1)}</Tag>
      : <Fragment key={i}>{part}</Fragment>,
  )
}

/** Keep line breaks typed in the admin as <br />. */
export function lines(text: string): ReactNode {
  return (text ?? '').split('\n').map((line, i, arr) => (
    <Fragment key={i}>{line}{i < arr.length - 1 && <br />}</Fragment>
  ))
}
