import { useState, type FormEvent } from 'react'
import { publicApi, resumeUrl } from '../../api/client'
import type { ContactSection, SiteSection } from '../../api/types'
import { rich } from '../../lib/rich'
import Reveal from './Reveal'

type Status = { kind: 'idle' | 'sending' | 'sent' | 'error'; text?: string }
const EMPTY = { name: '', email: '', subject: '', body: '', website: '' }

export default function Contact({ contact, site, resumeAvailable }: {
  contact: ContactSection; site: SiteSection; resumeAvailable: boolean
}) {
  const [form, setForm] = useState(EMPTY)
  const [status, setStatus] = useState<Status>({ kind: 'idle' })
  const set = (k: keyof typeof EMPTY) => (e: { target: { value: string } }) => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setStatus({ kind: 'sending' })
    try {
      await publicApi.sendMessage(form)
      setForm(EMPTY)
      setStatus({ kind: 'sent', text: 'Message received — I’ll get back to you soon.' })
    } catch (err) {
      setStatus({ kind: 'error', text: err instanceof Error ? err.message : 'Something went wrong' })
    }
  }

  const socials = [
    site.email && { href: `mailto:${site.email}`, label: site.email },
    site.linkedin && { href: site.linkedin, label: 'LinkedIn ↗' },
    site.github && { href: site.github, label: 'GitHub ↗' },
  ].filter(Boolean) as { href: string; label: string }[]

  return (
    <section className="contact" id="contact">
      <div className="shell">
        <Reveal className="contact__panel">
          <div className="contact__top"><span>{contact.index}</span><span>{contact.tagline}</span></div>
          <h2 className="contact__title">{rich(contact.title, 'span')}</h2>

          {contact.form_enabled && (
            <form className="contact-form" onSubmit={submit} noValidate={false}>
              <input placeholder="Your name" required maxLength={120} value={form.name} onChange={set('name')} aria-label="Your name" />
              <input placeholder="Email" type="email" required value={form.email} onChange={set('email')} aria-label="Email" />
              <input className="full" placeholder="Subject (optional)" maxLength={200} value={form.subject} onChange={set('subject')} aria-label="Subject" />
              <textarea placeholder="Tell me about the problem…" required minLength={5} maxLength={5000} value={form.body} onChange={set('body')} aria-label="Message" />
              <input className="hp" tabIndex={-1} autoComplete="off" value={form.website} onChange={set('website')} aria-hidden="true" />
              <div className="contact-form__row">
                <button className="button" type="submit" disabled={status.kind === 'sending'}>
                  {status.kind === 'sending' ? 'Sending…' : 'Send message →'}
                </button>
                {status.text && (
                  <span className={`contact-form__status ${status.kind === 'error' ? 'is-error' : ''}`} role="status">{status.text}</span>
                )}
              </div>
            </form>
          )}

          <div className="contact__bottom">
            <div>
              <p>{contact.body}</p>
              {socials.length > 0 && (
                <div className="contact__socials">
                  {socials.map(s => <a key={s.href} href={s.href} target={s.href.startsWith('http') ? '_blank' : undefined} rel="noreferrer">{s.label}</a>)}
                </div>
              )}
            </div>
            <div className="contact__links">
              {resumeAvailable && <a className="button" href={resumeUrl} download>Download résumé ↘</a>}
              <a className="button button--ghost" href="#top">Back to top ↑</a>
            </div>
          </div>
        </Reveal>
        <footer className="footer"><span>{site.footer_left}</span><span>{site.footer_right}</span></footer>
      </div>
    </section>
  )
}
