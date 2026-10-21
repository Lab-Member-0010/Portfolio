import { useEffect, useState, type ReactNode } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const NAV = [
  { to: '/admin', label: 'Dashboard', end: true },
  { to: '/admin/content', label: 'Page copy' },
  { to: '/admin/c/projects', label: 'Projects' },
  { to: '/admin/c/facts', label: 'Quick facts' },
  { to: '/admin/c/timeline', label: 'Experience' },
  { to: '/admin/c/skills', label: 'Skills' },
  { to: '/admin/c/certifications', label: 'Certifications' },
  { to: '/admin/c/life-cards', label: 'Beyond code' },
  { to: '/admin/messages', label: 'Messages' },
  { to: '/admin/resume', label: 'Résumé' },
  { to: '/admin/account', label: 'Account' },
]

export default function AdminLayout({ children }: { children: ReactNode }) {
  const { email, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const location = useLocation()
  useEffect(() => setOpen(false), [location.pathname])

  return (
    <div className={`adm-shell ${open ? 'is-open' : ''}`}>
      <aside className="adm-side">
        <div className="adm-brand">JS<span>/</span>admin</div>
        <nav>
          {NAV.map(n => (
            <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => `adm-nav ${isActive ? 'is-active' : ''}`}>
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="adm-side__foot">
          <a className="adm-nav" href="/" target="_blank" rel="noreferrer">View site ↗</a>
          <div className="adm-muted adm-small">{email}</div>
          <button className="adm-btn adm-btn--ghost adm-btn--block" onClick={logout}>Log out</button>
        </div>
      </aside>
      <div className="adm-main">
        <header className="adm-topbar">
          <button className="adm-btn adm-btn--ghost adm-menu" onClick={() => setOpen(o => !o)} aria-label="Toggle menu">☰</button>
          <span className="adm-brand adm-brand--sm">JS<span>/</span>admin</span>
        </header>
        <div className="adm-content">{children}</div>
      </div>
      <div className="adm-scrim" onClick={() => setOpen(false)} />
    </div>
  )
}
