import type { ElementType, ReactNode } from 'react'
import { useInView } from '../../hooks/useInView'

interface Props { as?: ElementType; className?: string; children: ReactNode }

export default function Reveal({ as: Tag = 'div', className = '', children }: Props) {
  const { ref, inView } = useInView<HTMLElement>()
  return <Tag ref={ref} className={`reveal ${inView ? 'is-visible' : ''} ${className}`.trim()}>{children}</Tag>
}
