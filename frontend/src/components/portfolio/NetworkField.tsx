import { useEffect, useRef } from 'react'
import { prefersReducedMotion } from '../../hooks/useReducedMotion'

/** A quiet network field that responds to the visitor, hinting at connected systems. */
export default function NetworkField() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || prefersReducedMotion()) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    type Pt = { x: number; y: number; vx: number; vy: number }
    let points: Pt[] = []
    let frame = 0
    const mouse = { x: -1000, y: -1000 }

    const resize = () => {
      const scale = Math.min(window.devicePixelRatio || 1, 2)
      canvas.width = window.innerWidth * scale
      canvas.height = window.innerHeight * scale
      canvas.style.width = `${window.innerWidth}px`
      canvas.style.height = `${window.innerHeight}px`
      ctx.setTransform(scale, 0, 0, scale, 0, 0)
      points = Array.from({ length: Math.min(46, Math.floor(window.innerWidth / 24)) }, () => ({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.15,
      }))
    }
    const onMove = (e: MouseEvent) => { mouse.x = e.clientX; mouse.y = e.clientY }

    const draw = () => {
      const w = window.innerWidth, h = window.innerHeight
      ctx.clearRect(0, 0, w, h)
      points.forEach((p, i) => {
        p.x += p.vx; p.y += p.vy
        if (p.x < 0 || p.x > w) p.vx *= -1
        if (p.y < 0 || p.y > h) p.vy *= -1
        const md = Math.hypot(p.x - mouse.x, p.y - mouse.y)
        if (md < 190) {
          ctx.beginPath()
          ctx.strokeStyle = `rgba(200,255,46,${(1 - md / 190) * 0.28})`
          ctx.moveTo(p.x, p.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke()
        }
        for (let j = i + 1; j < points.length; j += 1) {
          const o = points[j]
          const d = Math.hypot(p.x - o.x, p.y - o.y)
          if (d < 110) {
            ctx.beginPath()
            ctx.strokeStyle = `rgba(242,240,232,${(1 - d / 110) * 0.08})`
            ctx.moveTo(p.x, p.y); ctx.lineTo(o.x, o.y); ctx.stroke()
          }
        }
        ctx.beginPath()
        ctx.fillStyle = 'rgba(242,240,232,.22)'
        ctx.arc(p.x, p.y, 1.1, 0, Math.PI * 2)
        ctx.fill()
      })
      frame = requestAnimationFrame(draw)
    }

    window.addEventListener('mousemove', onMove, { passive: true })
    window.addEventListener('resize', resize)
    resize(); draw()
    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return <canvas id="field" ref={canvasRef} aria-hidden="true" />
}
