import type { HeadSection, Skill } from '../../api/types'
import Reveal from './Reveal'
import SectionHead from './SectionHead'

export default function Arsenal({ head, skills }: { head: HeadSection; skills: Skill[] }) {
  return (
    <section className="arsenal" id="arsenal">
      <div className="shell">
        <SectionHead {...head} />
        <Reveal className="skill-grid">
          {skills.map((s, i) => (
            <div className="skill-card" data-glyph={s.glyph} key={s.id}>
              <span className="skill-card__num">{String(i + 1).padStart(2, '0')}</span>
              <h3>{s.title}</h3>
              <p>{s.items}</p>
            </div>
          ))}
        </Reveal>
      </div>
    </section>
  )
}
