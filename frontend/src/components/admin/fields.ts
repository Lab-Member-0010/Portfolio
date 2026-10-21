export type FieldType = 'text' | 'textarea' | 'bool' | 'tags' | 'lines' | 'select' | 'number'

export interface FieldDef {
  name: string
  label: string
  type?: FieldType
  options?: { value: string; label: string }[]
  help?: string
  required?: boolean
  wide?: boolean
}

const RICH = 'Wrap words in *asterisks* to highlight them.'

export const SECTION_FIELDS: Record<string, { title: string; fields: FieldDef[] }> = {
  site: {
    title: 'Site & navigation',
    fields: [
      { name: 'nav_mark', label: 'Nav mark' },
      { name: 'nav_cta', label: 'Nav button label' },
      { name: 'meta_title', label: 'Browser title', wide: true },
      { name: 'meta_description', label: 'Meta description', type: 'textarea', wide: true },
      { name: 'email', label: 'Public email' },
      { name: 'linkedin', label: 'LinkedIn URL' },
      { name: 'github', label: 'GitHub URL' },
      { name: 'marquee', label: 'Marquee items', type: 'lines', help: 'One item per line.', wide: true },
      { name: 'footer_left', label: 'Footer left' },
      { name: 'footer_right', label: 'Footer right' },
    ],
  },
  hero: {
    title: 'Hero',
    fields: [
      { name: 'first_name', label: 'First name' },
      { name: 'last_name', label: 'Last name (outlined)' },
      { name: 'accent_letter', label: 'Accent letter(s) in last name' },
      { name: 'available', label: 'Show “available” signal', type: 'bool' },
      { name: 'eyebrow', label: 'Eyebrow', wide: true },
      { name: 'coordinates', label: 'Coordinates', type: 'textarea' },
      { name: 'stamp_kanji', label: 'Stamp kanji' },
      { name: 'stamp_text', label: 'Stamp text', type: 'textarea' },
      { name: 'statement', label: 'Statement', type: 'textarea', help: RICH, wide: true },
      { name: 'primary_cta', label: 'Primary button' },
      { name: 'resume_cta', label: 'Résumé button' },
    ],
  },
  about: {
    title: 'About',
    fields: [
      { name: 'index', label: 'Section index' },
      { name: 'title', label: 'Title', help: RICH, wide: true },
      { name: 'manifesto', label: 'Manifesto', type: 'textarea', help: RICH, wide: true },
    ],
  },
  work: { title: 'Work heading', fields: [{ name: 'index', label: 'Section index' }, { name: 'title', label: 'Title', help: RICH, wide: true }] },
  experience: {
    title: 'Experience',
    fields: [
      { name: 'index', label: 'Section index' },
      { name: 'title', label: 'Title', help: RICH, wide: true },
      { name: 'company', label: 'Company' },
      { name: 'role', label: 'Role · location' },
      { name: 'period', label: 'Period' },
      { name: 'years', label: 'Big number' },
      { name: 'years_caption', label: 'Big number caption', wide: true },
    ],
  },
  arsenal: { title: 'Arsenal heading', fields: [{ name: 'index', label: 'Section index' }, { name: 'title', label: 'Title', help: RICH, wide: true }] },
  credentials: { title: 'Credentials heading', fields: [{ name: 'index', label: 'Section index' }, { name: 'title', label: 'Title', help: RICH, wide: true }] },
  offscreen: { title: 'Beyond-code heading', fields: [{ name: 'index', label: 'Section index' }, { name: 'title', label: 'Title', help: RICH, wide: true }] },
  contact: {
    title: 'Contact',
    fields: [
      { name: 'index', label: 'Section index' },
      { name: 'tagline', label: 'Tagline' },
      { name: 'title', label: 'Title', help: RICH, wide: true },
      { name: 'body', label: 'Body', type: 'textarea', wide: true },
      { name: 'form_enabled', label: 'Show contact form', type: 'bool' },
    ],
  },
}

export interface CollectionDef {
  title: string
  singular: string
  primary: string
  secondary?: string
  /** items can carry an uploaded PDF (certifications) */
  files?: boolean
  fields: FieldDef[]
}

export const COLLECTIONS: Record<string, CollectionDef> = {
  projects: {
    title: 'Projects', singular: 'project', primary: 'title', secondary: 'category',
    fields: [
      { name: 'title', label: 'Title', required: true },
      { name: 'code', label: 'Code (e.g. P/06)', help: 'Leave blank to auto-number.' },
      { name: 'category', label: 'Category', wide: true },
      { name: 'summary', label: 'Summary', type: 'textarea', wide: true },
      { name: 'impact', label: 'Impact line', type: 'textarea', wide: true },
      { name: 'tags', label: 'Tech tags', type: 'tags', help: 'Comma-separated.', wide: true },
      { name: 'link', label: 'Link (optional)', wide: true },
    ],
  },
  facts: {
    title: 'Quick facts', singular: 'fact', primary: 'value', secondary: 'label',
    fields: [
      { name: 'value', label: 'Value', required: true, help: 'Numbers animate as a count-up.' },
      { name: 'suffix', label: 'Suffix (e.g. +)' },
      { name: 'label', label: 'Label', required: true, wide: true },
    ],
  },
  timeline: {
    title: 'Experience timeline', singular: 'milestone', primary: 'title', secondary: 'body',
    fields: [
      { name: 'title', label: 'Title', required: true, wide: true },
      { name: 'body', label: 'Description', type: 'textarea', wide: true },
    ],
  },
  skills: {
    title: 'Skills', singular: 'skill group', primary: 'title', secondary: 'items',
    fields: [
      { name: 'title', label: 'Title', required: true },
      { name: 'glyph', label: 'Background glyph' },
      { name: 'items', label: 'Items', type: 'textarea', help: 'Separate with “ · ”.', wide: true },
    ],
  },
  certifications: {
    title: 'Certifications & training', singular: 'credential', primary: 'title', secondary: 'issuer', files: true,
    fields: [
      {
        name: 'kind', label: 'Type', type: 'select',
        options: [{ value: 'certification', label: 'Certification' }, { value: 'training', label: 'Training programme' }],
      },
      { name: 'issued', label: 'Issued / period', help: 'e.g. Oct 2026 or 2024 — 2025' },
      { name: 'title', label: 'Title', required: true, wide: true },
      { name: 'issuer', label: 'Issuer' },
      { name: 'credential_id', label: 'Credential ID' },
      { name: 'summary', label: 'Summary', type: 'textarea', wide: true },
      { name: 'link', label: 'Verification link (optional)', wide: true, help: 'Certificate PDFs are uploaded from the list with “Upload PDF”.' },
    ],
  },
  'life-cards': {
    title: 'Beyond code', singular: 'card', primary: 'title', secondary: 'label',
    fields: [
      {
        name: 'variant', label: 'Style', type: 'select',
        options: [
          { value: 'chess', label: 'Lime / chess board (tall)' },
          { value: 'travel', label: 'Sky / route' },
          { value: 'japan', label: 'Red / vertical text' },
          { value: 'plain', label: 'Plain dark' },
        ],
      },
      { name: 'label', label: 'Label' },
      { name: 'title', label: 'Title', required: true, wide: true },
      { name: 'body', label: 'Body', type: 'textarea', wide: true },
      { name: 'decor', label: 'Decoration text', help: 'Knight glyph, travel code, or Japanese text.' },
    ],
  },
}
