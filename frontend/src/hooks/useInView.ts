import { useEffect, useRef, useState } from 'react'

/** Flips to true once the element enters the viewport (and stays true). */
export function useInView<T extends Element>(threshold = 0.12) {
  const ref = useRef<T | null>(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el || inView) return
    if (typeof IntersectionObserver === 'undefined') { setInView(true); return }
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) { setInView(true); io.disconnect() }
    }, { threshold })
    io.observe(el)
    return () => io.disconnect()
  }, [threshold, inView])
  return { ref, inView }
}
