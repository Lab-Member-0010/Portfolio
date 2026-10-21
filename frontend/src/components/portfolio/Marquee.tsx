import { Fragment } from 'react'

export default function Marquee({ items }: { items: string[] }) {
  if (!items.length) return null
  const track = (
    <span>
      {items.map((item, i) => <Fragment key={i}>{item} <b>✦</b> </Fragment>)}
    </span>
  )
  return (
    <div className="marquee" aria-hidden="true">
      <div className="marquee__track">{track}{track}</div>
    </div>
  )
}
