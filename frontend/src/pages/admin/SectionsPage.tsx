import { useEffect, useState, type FormEvent } from 'react'
import { adminApi } from '../../api/client'
import type { SectionKey, Sections } from '../../api/types'
import FieldInput, { cleanForSubmit } from '../../components/admin/FieldInput'
import { SECTION_FIELDS } from '../../components/admin/fields'
import { useToast } from '../../context/ToastContext'

type Data = Record<string, string | number | boolean | string[] | undefined>

function SectionForm({ sectionKey, initial }: { sectionKey: SectionKey; initial: Data }) {
  const def = SECTION_FIELDS[sectionKey]
  const [data, setData] = useState<Data>(initial)
  const [busy, setBusy] = useState(false)
  const [dirty, setDirty] = useState(false)
  const toast = useToast()

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    try {
      const saved = await adminApi.saveSection(sectionKey, cleanForSubmit(def.fields, data) as never)
      setData(saved as unknown as Data); setDirty(false)
      toast(`${def.title} saved`)
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Save failed', 'error')
    } finally { setBusy(false) }
  }

  return (
    <form className="adm-card adm-section" onSubmit={submit} id={`section-${sectionKey}`}>
      <div className="adm-section__head">
        <h3>{def.title}</h3>
        <button className="adm-btn adm-btn--primary" disabled={busy || !dirty}>{busy ? 'Saving…' : dirty ? 'Save' : 'Saved'}</button>
      </div>
      <div className="adm-grid">
        {def.fields.map(f => (
          <FieldInput key={f.name} field={f} value={data[f.name]} onChange={v => { setData(d => ({ ...d, [f.name]: v })); setDirty(true) }} />
        ))}
      </div>
    </form>
  )
}

export default function SectionsPage() {
  const [sections, setSections] = useState<Sections | null>(null)
  useEffect(() => { adminApi.sections().then(setSections).catch(() => {}) }, [])

  return (
    <>
      <div className="adm-head">
        <div><h1>Page copy</h1><p className="adm-muted">Each block saves independently.</p></div>
        <div className="adm-jump">
          {Object.entries(SECTION_FIELDS).map(([k, d]) => <a key={k} href={`#section-${k}`}>{d.title}</a>)}
        </div>
      </div>
      {!sections ? <div className="adm-muted">Loading…</div> :
        (Object.keys(SECTION_FIELDS) as SectionKey[]).map(k => (
          <SectionForm key={k} sectionKey={k} initial={sections[k] as unknown as Data} />
        ))}
    </>
  )
}
