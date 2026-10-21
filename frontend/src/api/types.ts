export interface Ordered {
  id: number
  sort_order: number
  is_published: boolean
}

export interface Fact extends Ordered { value: string; suffix: string; label: string }
export interface Project extends Ordered {
  code: string; title: string; category: string; summary: string; impact: string; tags: string[]; link: string
}
export interface TimelineItem extends Ordered { title: string; body: string }
export interface Skill extends Ordered { title: string; glyph: string; items: string }
export type LifeVariant = 'chess' | 'travel' | 'japan' | 'plain'
export interface LifeCard extends Ordered { variant: LifeVariant; label: string; title: string; body: string; decor: string }

export type CertKind = 'certification' | 'training'
export interface Certification extends Ordered {
  kind: CertKind; title: string; issuer: string; issued: string; credential_id: string; summary: string; link: string; has_file: boolean
}

export interface SiteSection {
  nav_mark: string; nav_cta: string; meta_title: string; meta_description: string
  email: string; linkedin: string; github: string; marquee: string[]; footer_left: string; footer_right: string
}
export interface HeroSection {
  eyebrow: string; available: boolean; coordinates: string; first_name: string; last_name: string; accent_letter: string
  stamp_kanji: string; stamp_text: string; statement: string; primary_cta: string; resume_cta: string
}
export interface HeadSection { index: string; title: string }
export interface AboutSection extends HeadSection { manifesto: string }
export interface ExperienceSection extends HeadSection {
  period: string; company: string; role: string; years: string; years_caption: string
}
export interface ContactSection extends HeadSection { tagline: string; body: string; form_enabled: boolean }

export interface Sections {
  site: SiteSection
  hero: HeroSection
  about: AboutSection
  work: HeadSection
  experience: ExperienceSection
  arsenal: HeadSection
  credentials: HeadSection
  offscreen: HeadSection
  contact: ContactSection
}
export type SectionKey = keyof Sections

export interface Portfolio {
  sections: Sections
  facts: Fact[]
  projects: Project[]
  timeline: TimelineItem[]
  skills: Skill[]
  life_cards: LifeCard[]
  certifications: Certification[]
  resume_available: boolean
}

export interface Message {
  id: number; name: string; email: string; subject: string; body: string; is_read: boolean; created_at: string
}

export interface ResumeInfo { available: boolean; size?: number; updated_at?: string }
export interface Stats { projects: number; skills: number; certifications: number; messages: number; unread_messages: number; resume: ResumeInfo }
