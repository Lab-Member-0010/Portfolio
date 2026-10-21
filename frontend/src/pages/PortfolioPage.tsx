import { useEffect, useState } from 'react'
import { publicApi } from '../api/client'
import type { Portfolio } from '../api/types'
import About from '../components/portfolio/About'
import Arsenal from '../components/portfolio/Arsenal'
import Credentials from '../components/portfolio/Credentials'
import Contact from '../components/portfolio/Contact'
import Experience from '../components/portfolio/Experience'
import Hero from '../components/portfolio/Hero'
import Marquee from '../components/portfolio/Marquee'
import Nav from '../components/portfolio/Nav'
import NetworkField from '../components/portfolio/NetworkField'
import Offscreen from '../components/portfolio/Offscreen'
import Projects from '../components/portfolio/Projects'
import { useScrollProgress } from '../hooks/useScrollProgress'
import '../styles/portfolio.css'

function setMeta(title: string, description: string) {
  if (title) document.title = title
  const tag = document.querySelector('meta[name="description"]')
  if (tag && description) tag.setAttribute('content', description)
}

export default function PortfolioPage() {
  const [data, setData] = useState<Portfolio | null>(null)
  const [error, setError] = useState<string | null>(null)
  const progressRef = useScrollProgress<HTMLDivElement>()

  useEffect(() => {
    publicApi.portfolio()
      .then(d => { setData(d); setMeta(d.sections.site.meta_title, d.sections.site.meta_description) })
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to load'))
  }, [])

  if (error) return <div className="loader">Couldn’t reach the API — {error}</div>
  if (!data) return <div className="loader">Loading <span>✦</span></div>

  const { sections: s } = data
  return (
    <>
      <NetworkField />
      <div className="noise" aria-hidden="true" />
      <div className="progress" ref={progressRef} aria-hidden="true" />
      <Nav site={s.site} />
      <main id="top">
        <Hero hero={s.hero} resumeAvailable={data.resume_available} />
        <Marquee items={s.site.marquee} />
        <About about={s.about} facts={data.facts} />
        <Projects head={s.work} projects={data.projects} />
        <Experience exp={s.experience} timeline={data.timeline} />
        <Arsenal head={s.arsenal} skills={data.skills} />
        <Credentials head={s.credentials} items={data.certifications} />
        <Offscreen head={s.offscreen} cards={data.life_cards} />
        <Contact contact={s.contact} site={s.site} resumeAvailable={data.resume_available} />
      </main>
    </>
  )
}
