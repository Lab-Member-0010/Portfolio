import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminApi } from '../../api/client'
import type { Stats } from '../../api/types'

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  useEffect(() => { adminApi.stats().then(setStats).catch(() => {}) }, [])

  const cards = stats ? [
    { label: 'Projects', value: stats.projects, to: '/admin/c/projects' },
    { label: 'Certifications', value: stats.certifications, to: '/admin/c/certifications' },
    { label: 'Unread messages', value: stats.unread_messages, to: '/admin/messages', hot: stats.unread_messages > 0 },
    { label: 'Résumé', value: stats.resume.available ? 'Live' : 'Missing', to: '/admin/resume', hot: !stats.resume.available },
  ] : []

  return (
    <>
      <div className="adm-head"><div><h1>Dashboard</h1><p className="adm-muted">Everything on the public site is editable from here.</p></div></div>
      {!stats ? <div className="adm-muted">Loading…</div> : (
        <div className="adm-stats">
          {cards.map(c => (
            <Link key={c.label} to={c.to} className={`adm-card adm-stat ${c.hot ? 'is-hot' : ''}`}>
              <strong>{c.value}</strong><span>{c.label}</span>
            </Link>
          ))}
        </div>
      )}
      <div className="adm-card adm-tips">
        <h3>Quick guide</h3>
        <ul>
          <li><b>Page copy</b> — hero, section headings, contact text, marquee and social links.</li>
          <li><b>Collections</b> — add, edit, hide, delete and reorder projects, facts, timeline, skills, certifications and life cards.</li>
          <li><b>Certifications</b> — use “Upload PDF” on a row to attach the certificate; visitors get a “View certificate” link.</li>
          <li>In titles, wrap words in <code>*asterisks*</code> to get the lime/serif highlight.</li>
          <li>Hidden items stay in the admin but don’t appear on the site.</li>
        </ul>
      </div>
    </>
  )
}
