import type { SiteSection } from '../../api/types'

const LINKS = [
  { href: '#about', label: 'About' },
  { href: '#work', label: 'Work' },
  { href: '#arsenal', label: 'Arsenal' },
  { href: '#credentials', label: 'Credentials' },
  { href: '#offscreen', label: 'Beyond code' },
]

export default function Nav({ site }: { site: SiteSection }) {
  return (
    <nav className="nav" aria-label="Primary navigation">
      <a className="nav__mark" href="#top">{site.nav_mark}</a>
      <div className="nav__links">
        {LINKS.map(l => <a key={l.href} href={l.href}>{l.label}</a>)}
      </div>
      <a className="nav__cta" href="#contact">{site.nav_cta}</a>
    </nav>
  )
}
