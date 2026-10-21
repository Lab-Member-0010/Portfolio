import { useState, type KeyboardEvent } from 'react'
import type { HeadSection, Project } from '../../api/types'
import Reveal from './Reveal'
import SectionHead from './SectionHead'

export default function Projects({ head, projects }: { head: HeadSection; projects: Project[] }) {
  const [openId, setOpenId] = useState<number | null>(projects[0]?.id ?? null)
  const toggle = (id: number) => setOpenId(cur => (cur === id ? null : id))
  const onKey = (e: KeyboardEvent, id: number) => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(id) }
  }

  return (
    <section className="projects" id="work">
      <div className="shell">
        <SectionHead {...head} />
        <Reveal className="project-list">
          {projects.map((p, i) => {
            const open = openId === p.id
            return (
              <article
                key={p.id}
                className={`project ${open ? 'is-open' : ''}`}
                tabIndex={0}
                role="button"
                aria-expanded={open}
                onClick={() => toggle(p.id)}
                onKeyDown={e => onKey(e, p.id)}
              >
                <div className="project__num">{p.code || `P/${String(i + 1).padStart(2, '0')}`}</div>
                <h3 className="project__title">{p.title}</h3>
                <div className="project__meta">{p.category}<br /><span className="project__toggle">+</span></div>
                <div className="project__detail">
                  <div>
                    <p>{p.summary}</p>
                    {p.impact && <p className="project__impact">{p.impact}</p>}
                    {p.link && (
                      <p className="project__impact">
                        <a href={p.link} target="_blank" rel="noreferrer" onClick={e => e.stopPropagation()}>Visit project ↗</a>
                      </p>
                    )}
                  </div>
                  <div className="chips">{p.tags.map(t => <span className="chip" key={t}>{t}</span>)}</div>
                </div>
              </article>
            )
          })}
        </Reveal>
      </div>
    </section>
  )
}
