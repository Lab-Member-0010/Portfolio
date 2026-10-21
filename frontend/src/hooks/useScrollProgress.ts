import { useEffect, useRef } from 'react'

/** Returns a ref for the top progress bar; width tracks page scroll without re-rendering. */
export function useScrollProgress<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  useEffect(() => {
    const update = () => {
      const range = document.documentElement.scrollHeight - window.innerHeight
      if (ref.current) ref.current.style.width = `${range > 0 ? (window.scrollY / range) * 100 : 0}%`
    }
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    update()
    return () => { window.removeEventListener('scroll', update); window.removeEventListener('resize', update) }
  }, [])
  return ref
}
