import type { HeroSection } from '../../api/types'
import { resumeUrl } from '../../api/client'
import { lines, rich } from '../../lib/rich'

function LastName({ name, accent }: { name: string; accent: string }) {
  const idx = accent ? name.toLowerCase().indexOf(accent.toLowerCase()) : -1
  if (idx < 0) return <>{name}</>
  return <>{name.slice(0, idx)}<span className="accent">{name.slice(idx, idx + accent.length)}</span>{name.slice(idx + accent.length)}</>
}

export default function Hero({ hero, resumeAvailable }: { hero: HeroSection; resumeAvailable: boolean }) {
  return (
    <header className="hero">
      <div className="shell">
        <div className="hero__topline">
          <div className="eyebrow">{hero.available && <span className="signal" />} {hero.eyebrow}</div>
          <div className="hero__coordinates">{hero.coordinates}</div>
        </div>

        <h1 className="hero__title">
          {hero.first_name}
          <span className="outline"><LastName name={hero.last_name} accent={hero.accent_letter} /></span>
        </h1>

        <div className="hero__stamp" aria-hidden="true">
          <span><strong>{hero.stamp_kanji}</strong><br />{lines(hero.stamp_text)}</span>
        </div>

        <div className="hero__bottom">
          <p className="hero__statement">{rich(hero.statement)}</p>
          <div className="hero__actions">
            <a className="button" href="#work">{hero.primary_cta}</a>
            {resumeAvailable && (
              <a className="button button--ghost" href={resumeUrl} download>{hero.resume_cta}</a>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
