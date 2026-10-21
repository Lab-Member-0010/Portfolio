import { useEffect, useState } from 'react'
import type { AboutSection, Fact } from '../../api/types'
import { useInView } from '../../hooks/useInView'
import { prefersReducedMotion } from '../../hooks/useReducedMotion'
import { rich } from '../../lib/rich'
import Reveal from './Reveal'
import SectionHead from './SectionHead'

function FactValue({ fact, start }: { fact: Fact; start: boolean }) {
  const target = /^\d+$/.test(fact.value) ? Number(fact.value) : null
  const [n, setN] = useState(0)
  useEffect(() => {
    if (!start || target === null) return
    if (prefersReducedMotion()) { setN(target); return }
    let v = 0
    const id = window.setInterval(() => {
      v += 1
      setN(Math.min(v, target))
      if (v >= target) window.clearInterval(id)
    }, 110)
    return () => window.clearInterval(id)
  }, [start, target])
  if (target === null) return <strong>{fact.value}{fact.suffix}</strong>
  return <strong>{n}{n === target ? fact.suffix : ''}</strong>
}

export default function About({ about, facts }: { about: AboutSection; facts: Fact[] }) {
  const { ref, inView } = useInView<HTMLDivElement>(0.5)
  return (
    <section id="about">
      <div className="shell">
        <SectionHead index={about.index} title={about.title} />
        <Reveal className="manifesto">
          <div className="manifesto__copy"><p>{rich(about.manifesto, 'span')}</p></div>
          <div className="manifesto__facts" ref={ref}>
            {facts.map(f => (
              <div className="fact" key={f.id}><FactValue fact={f} start={inView} /><span>{f.label}</span></div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}
