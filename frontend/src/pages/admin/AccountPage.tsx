import { useState, type FormEvent } from 'react'
import { authApi } from '../../api/client'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'

export default function AccountPage() {
  const { email } = useAuth()
  const toast = useToast()
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (next !== confirm) { setError('New passwords don’t match'); return }
    try {
      await authApi.changePassword(current, next)
      setCurrent(''); setNext(''); setConfirm('')
      toast('Password changed')
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed') }
  }

  return (
    <>
      <div className="adm-head"><div><h1>Account</h1><p className="adm-muted">Signed in as {email}</p></div></div>
      <form className="adm-card adm-section adm-narrow" onSubmit={submit}>
        <h3>Change password</h3>
        <div className="adm-grid">
          <div className="adm-field adm-field--wide"><label htmlFor="cur">Current password</label>
            <input id="cur" type="password" required value={current} onChange={e => setCurrent(e.target.value)} autoComplete="current-password" /></div>
          <div className="adm-field adm-field--wide"><label htmlFor="new">New password</label>
            <input id="new" type="password" required minLength={8} maxLength={72} value={next} onChange={e => setNext(e.target.value)} autoComplete="new-password" /></div>
          <div className="adm-field adm-field--wide"><label htmlFor="conf">Confirm new password</label>
            <input id="conf" type="password" required value={confirm} onChange={e => setConfirm(e.target.value)} autoComplete="new-password" /></div>
        </div>
        {error && <div className="adm-error">{error}</div>}
        <div className="adm-actions adm-actions--left"><button className="adm-btn adm-btn--primary">Update password</button></div>
      </form>
    </>
  )
}
