import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'

type Toast = { id: number; text: string; kind: 'ok' | 'error' }
const ToastContext = createContext<(text: string, kind?: Toast['kind']) => void>(() => {})

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const push = useCallback((text: string, kind: Toast['kind'] = 'ok') => {
    const id = Date.now() + Math.random()
    setToasts(t => [...t, { id, text, kind }])
    window.setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3200)
  }, [])
  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="adm-toasts" role="status" aria-live="polite">
        {toasts.map(t => <div key={t.id} className={`adm-toast adm-toast--${t.kind}`}>{t.text}</div>)}
      </div>
    </ToastContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useToast = () => useContext(ToastContext)
