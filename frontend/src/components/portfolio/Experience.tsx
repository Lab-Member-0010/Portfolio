import type { ExperienceSection, TimelineItem } from '../../api/types'
import Reveal from './Reveal'
import SectionHead from './SectionHead'

export default function Experience({ exp, timeline }: { exp: ExperienceSection; timeline: TimelineItem[] }) {
  return (
    <section id="experience">
      <div className="shell">
        <SectionHead index={exp.index} title={exp.title} />
        <div className="experience__grid">
          <Reveal className="experience__company">
            <div className="eyebrow">{exp.period}</div>
            <h3>{exp.company}</h3>
            <p>{exp.role}</p>
            <div className="years">{exp.years}<small>{exp.years_caption}</small></div>
          </Reveal>
          <Reveal className="timeline">
            {timeline.map((t, i) => (
              <div className="timeline__item" key={t.id}>
                <i>{String(i + 1).padStart(2, '0')}</i>
                <div><h4>{t.title}</h4><p>{t.body}</p></div>
              </div>
            ))}
          </Reveal>
        </div>
      </div>
    </section>
  )
}
