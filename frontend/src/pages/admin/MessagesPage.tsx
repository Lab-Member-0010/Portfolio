import { useEffect, useState } from 'react'
import { adminApi } from '../../api/client'
import type { Message } from '../../api/types'
import { useToast } from '../../context/ToastContext'

export default function MessagesPage() {
  const [messages, setMessages] = useState<Message[] | null>(null)
  const [openId, setOpenId] = useState<number | null>(null)
  const toast = useToast()

  useEffect(() => { adminApi.messages().then(setMessages).catch(e => toast(e.message, 'error')) }, [toast])

  const patch = (m: Message) => setMessages(list => list?.map(x => (x.id === m.id ? m : x)) ?? null)

  const open = async (m: Message) => {
    setOpenId(openId === m.id ? null : m.id)
    if (!m.is_read) patch(await adminApi.markMessage(m.id, true))
  }
  const toggleRead = async (m: Message) => patch(await adminApi.markMessage(m.id, !m.is_read))
  const remove = async (id: number) => {
    await adminApi.deleteMessage(id)
    setMessages(list => list?.filter(x => x.id !== id) ?? null)
    toast('Message deleted')
  }

  return (
    <>
      <div className="adm-head"><div><h1>Messages</h1><p className="adm-muted">Submissions from the contact form.</p></div></div>
      {!messages ? <div className="adm-muted">Loading…</div> : messages.length === 0 ? (
        <div className="adm-card adm-empty">No messages yet.</div>
      ) : (
        <ul className="adm-list">
          {messages.map(m => (
            <li key={m.id} className={`adm-card adm-msg ${m.is_read ? '' : 'is-unread'}`}>
              <button className="adm-msg__head" onClick={() => open(m)} aria-expanded={openId === m.id}>
                <span className="adm-dot" />
                <strong>{m.name}</strong>
                <span className="adm-muted adm-msg__subject">{m.subject || m.body.slice(0, 80)}</span>
                <span className="adm-muted adm-small">{new Date(m.created_at).toLocaleString()}</span>
              </button>
              {openId === m.id && (
                <div className="adm-msg__body">
                  <p className="adm-muted"><a className="adm-link" href={`mailto:${m.email}?subject=${encodeURIComponent('Re: ' + (m.subject || 'your message'))}`}>{m.email}</a></p>
                  <p className="adm-pre">{m.body}</p>
                  <div className="adm-actions adm-actions--left">
                    <a className="adm-btn adm-btn--primary" href={`mailto:${m.email}?subject=${encodeURIComponent('Re: ' + (m.subject || 'your message'))}`}>Reply</a>
                    <button className="adm-btn adm-btn--ghost" onClick={() => toggleRead(m)}>Mark {m.is_read ? 'unread' : 'read'}</button>
                    <button className="adm-btn adm-btn--danger" onClick={() => remove(m.id)}>Delete</button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  )
}
