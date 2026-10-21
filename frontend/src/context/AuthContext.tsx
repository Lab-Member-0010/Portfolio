import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { authApi, setUnauthorizedHandler, tokenStore } from '../api/client'

interface AuthState {
  email: string | null
  ready: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  const logout = useCallback(() => { tokenStore.clear(); setEmail(null) }, [])

  useEffect(() => {
    setUnauthorizedHandler(logout)
    if (!tokenStore.get()) { setReady(true); return }
    authApi.me().then(u => setEmail(u.email)).catch(logout).finally(() => setReady(true))
    return () => setUnauthorizedHandler(null)
  }, [logout])

  const login = useCallback(async (e: string, p: string) => {
    const { access_token } = await authApi.login(e, p)
    tokenStore.set(access_token)
    const me = await authApi.me()
    setEmail(me.email)
  }, [])

  const value = useMemo(() => ({ email, ready, login, logout }), [email, ready, login, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
