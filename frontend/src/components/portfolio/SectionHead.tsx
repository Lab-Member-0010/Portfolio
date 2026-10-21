import type { HeadSection } from '../../api/types'
import { rich } from '../../lib/rich'
import Reveal from './Reveal'

export default function SectionHead({ index, title }: HeadSection) {
  return (
    <Reveal className="section-head">
      <div className="section-index">{index}</div>
      <h2 className="section-title">{rich(title)}</h2>
    </Reveal>
  )
}
