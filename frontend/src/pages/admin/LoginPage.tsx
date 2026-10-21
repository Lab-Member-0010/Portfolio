import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function LoginPage() {
  const { email: current, login, ready } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (ready && current) return <Navigate to="/admin" replace />

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true); setError(null)
    try {
      await login(email, password)
      navigate('/admin', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally { setBusy(false) }
  }

  return (
    <div className="adm-login">
      <form className="adm-card adm-login__card" onSubmit={submit}>
        <div className="adm-brand">JS<span>/</span>admin</div>
        <h1>Sign in</h1>
        <p className="adm-muted">Manage the content of your portfolio.</p>
        <div className="adm-field adm-field--wide">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} />
        </div>
        <div className="adm-field adm-field--wide">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        {error && <div className="adm-error">{error}</div>}
        <button className="adm-btn adm-btn--primary adm-btn--block" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
        <Link className="adm-link" to="/">← Back to portfolio</Link>
      </form>
    </div>
  )
}
