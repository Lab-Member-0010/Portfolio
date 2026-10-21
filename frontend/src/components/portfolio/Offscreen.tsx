import type { HeadSection, LifeCard } from '../../api/types'
import Reveal from './Reveal'
import SectionHead from './SectionHead'

const SQUARES = Array.from({ length: 64 }, (_, i) => (Math.floor(i / 8) + i) % 2 === 1)

function Decor({ card }: { card: LifeCard }) {
  switch (card.variant) {
    case 'chess':
      return (
        <>
          <div className="board" aria-hidden="true">
            {SQUARES.map((dark, i) => <span key={i} className={`square ${dark ? 'dark' : ''}`} />)}
          </div>
          <div className="knight" aria-hidden="true">{card.decor || '♞'}</div>
        </>
      )
    case 'travel':
      return (
        <>
          <div className="route" aria-hidden="true" />
          <div className="travel-code" aria-hidden="true">{card.decor}</div>
        </>
      )
    case 'japan':
      return <div className="japanese" aria-hidden="true">{card.decor}</div>
    default:
      return card.decor ? <div className="life-card__kanji" aria-hidden="true">{card.decor}</div> : null
  }
}

const VARIANT_CLASS: Record<LifeCard['variant'], string> = {
  chess: 'life-card--wide', travel: 'life-card--travel', japan: 'life-card--japan', plain: '',
}

export default function Offscreen({ head, cards }: { head: HeadSection; cards: LifeCard[] }) {
  if (!cards.length) return null
  return (
    <section className="offscreen" id="offscreen">
      <div className="shell">
        <SectionHead {...head} />
        <Reveal className="life-grid">
          {cards.map(card => (
            <article key={card.id} className={`life-card ${VARIANT_CLASS[card.variant]}`}>
              <div className="life-card__label">{card.label}</div>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
              <Decor card={card} />
            </article>
          ))}
        </Reveal>
      </div>
    </section>
  )
}
