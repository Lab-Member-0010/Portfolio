import { certificateUrl } from '../../api/client'
import type { Certification, HeadSection } from '../../api/types'
import Reveal from './Reveal'
import SectionHead from './SectionHead'

export default function Credentials({ head, items }: { head: HeadSection; items: Certification[] }) {
  if (!items.length) return null
  return (
    <section className="credentials" id="credentials">
      <div className="shell">
        <SectionHead {...head} />
        <Reveal className="cred-list">
          {items.map((c, i) => {
            const href = c.has_file ? certificateUrl(c.id) : c.link
            return (
              <article className={`cred cred--${c.kind}`} key={c.id}>
                <div className="cred__num">C/{String(i + 1).padStart(2, '0')}</div>
                <div className="cred__body">
                  <span className="cred__kind">{c.kind === 'training' ? 'Training programme' : 'Certification'}</span>
                  <h3 className="cred__title">{c.title}</h3>
                  {c.issuer && <p className="cred__issuer">{c.issuer}</p>}
                  {c.summary && <p className="cred__summary">{c.summary}</p>}
                </div>
                <div className="cred__meta">
                  {c.issued && <span>{c.issued}</span>}
                  {c.credential_id && <span className="cred__id">ID · {c.credential_id}</span>}
                  {href && (
                    <a className="cred__link" href={href} target="_blank" rel="noreferrer">
                      {c.has_file ? 'View certificate ↗' : 'Verify ↗'}
                    </a>
                  )}
                </div>
              </article>
            )
          })}
        </Reveal>
      </div>
    </section>
  )
}
