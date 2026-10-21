import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { Navigate, useParams } from 'react-router-dom'
import { adminApi, certificateUrl, type CollectionName } from '../../api/client'
import type { Ordered } from '../../api/types'
import FieldInput, { cleanForSubmit } from '../../components/admin/FieldInput'
import { COLLECTIONS, type CollectionDef } from '../../components/admin/fields'
import { useToast } from '../../context/ToastContext'

type Item = Ordered & Record<string, unknown>
type Draft = Record<string, string | number | boolean | string[] | undefined>

function blank(def: CollectionDef): Draft {
  const d: Draft = { is_published: true }
  def.fields.forEach(f => {
    d[f.name] = f.type === 'tags' || f.type === 'lines' ? [] : f.type === 'bool' ? false : f.type === 'select' ? f.options?.[0]?.value : ''
  })
  return d
}

function Editor({ def, initial, onCancel, onSave }: {
  def: CollectionDef; initial: Draft; onCancel: () => void; onSave: (d: Draft) => Promise<void>
}) {
  const [draft, setDraft] = useState<Draft>(initial)
  const [busy, setBusy] = useState(false)
  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    try { await onSave(cleanForSubmit(def.fields, draft)) } finally { setBusy(false) }
  }
  return (
    <div className="adm-modal" role="dialog" aria-modal="true">
      <form className="adm-card adm-modal__card" onSubmit={submit}>
        <div className="adm-section__head">
          <h3>{initial.id ? `Edit ${def.singular}` : `New ${def.singular}`}</h3>
          <button type="button" className="adm-btn adm-btn--ghost" onClick={onCancel}>✕</button>
        </div>
        <div className="adm-grid">
          {def.fields.map(f => (
            <FieldInput key={f.name} field={f} value={draft[f.name]} onChange={v => setDraft(d => ({ ...d, [f.name]: v }))} />
          ))}
          <FieldInput field={{ name: 'is_published', label: 'Published (visible on site)', type: 'bool' }}
            value={draft.is_published} onChange={v => setDraft(d => ({ ...d, is_published: v }))} />
        </div>
        <div className="adm-actions">
          <button type="button" className="adm-btn adm-btn--ghost" onClick={onCancel}>Cancel</button>
          <button className="adm-btn adm-btn--primary" disabled={busy}>{busy ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </div>
  )
}

function FileControls({ item, onChange, onError }: {
  item: Item; onChange: (i: Item) => void; onError: (e: unknown) => void
}) {
  const input = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const upload = async (file?: File) => {
    if (!file) return
    setBusy(true)
    try { onChange(await adminApi.uploadCertificateFile<Item>(item.id, file)) } catch (e) { onError(e) }
    finally { setBusy(false); if (input.current) input.current.value = '' }
  }
  const remove = async () => {
    try { onChange(await adminApi.deleteCertificateFile<Item>(item.id)) } catch (e) { onError(e) }
  }
  return (
    <>
      {item.has_file && <a className="adm-btn adm-btn--ghost" href={certificateUrl(item.id)} target="_blank" rel="noreferrer">PDF ↗</a>}
      <button className="adm-btn adm-btn--ghost" onClick={() => input.current?.click()} disabled={busy}>
        {busy ? 'Uploading…' : item.has_file ? 'Replace PDF' : 'Upload PDF'}
      </button>
      {item.has_file && <button className="adm-btn adm-btn--ghost" onClick={remove} aria-label="Remove PDF">✕ PDF</button>}
      <input ref={input} type="file" accept="application/pdf" hidden onChange={e => upload(e.target.files?.[0])} />
    </>
  )
}

export default function CollectionPage() {
  const { collection = '' } = useParams()
  const def = COLLECTIONS[collection]
  const name = collection as CollectionName
  const toast = useToast()
  const [items, setItems] = useState<Item[] | null>(null)
  const [editing, setEditing] = useState<Draft | null>(null)
  const [confirmId, setConfirmId] = useState<number | null>(null)

  const load = useCallback(() => {
    setItems(null)
    adminApi.list<Item>(name).then(setItems).catch(e => toast(e.message, 'error'))
  }, [name, toast])
  useEffect(() => { if (def) load() }, [def, load])

  if (!def) return <Navigate to="/admin" replace />

  const fail = (e: unknown) => toast(e instanceof Error ? e.message : 'Request failed', 'error')

  const save = async (d: Draft) => {
    try {
      const { id, ...body } = d
      if (id) await adminApi.update(name, Number(id), { ...body, sort_order: d.sort_order ?? 0 })
      else await adminApi.create(name, body)
      toast(`${def.singular[0].toUpperCase()}${def.singular.slice(1)} saved`)
      setEditing(null); load()
    } catch (e) { fail(e) }
  }

  const togglePublish = async (item: Item) => {
    try {
      const updated = await adminApi.update<Item>(name, item.id, { ...item, is_published: !item.is_published })
      setItems(list => list?.map(i => (i.id === item.id ? updated : i)) ?? null)
    } catch (e) { fail(e) }
  }

  const remove = async (id: number) => {
    try {
      await adminApi.remove(name, id)
      setItems(list => list?.filter(i => i.id !== id) ?? null)
      setConfirmId(null); toast('Deleted')
    } catch (e) { fail(e) }
  }

  const move = async (index: number, dir: -1 | 1) => {
    if (!items) return
    const next = [...items]
    const j = index + dir
    if (j < 0 || j >= next.length) return
    ;[next[index], next[j]] = [next[j], next[index]]
    setItems(next)
    try { setItems(await adminApi.reorder<Item>(name, next.map(i => i.id))) } catch (e) { fail(e); load() }
  }

  return (
    <>
      <div className="adm-head">
        <div><h1>{def.title}</h1><p className="adm-muted">Use the arrows to change the order shown on the site.</p></div>
        <button className="adm-btn adm-btn--primary" onClick={() => setEditing(blank(def))}>+ Add {def.singular}</button>
      </div>

      {!items ? <div className="adm-muted">Loading…</div> : items.length === 0 ? (
        <div className="adm-card adm-empty">Nothing here yet.</div>
      ) : (
        <ul className="adm-list">
          {items.map((item, i) => (
            <li key={item.id} className={`adm-card adm-row ${item.is_published ? '' : 'is-hidden'}`}>
              <div className="adm-row__order">
                <button className="adm-icon" onClick={() => move(i, -1)} disabled={i === 0} aria-label="Move up">↑</button>
                <button className="adm-icon" onClick={() => move(i, 1)} disabled={i === items.length - 1} aria-label="Move down">↓</button>
              </div>
              <div className="adm-row__body">
                <strong>{String(item[def.primary] ?? '')}</strong>
                {def.secondary && <span className="adm-muted">{String(item[def.secondary] ?? '')}</span>}
              </div>
              <div className="adm-row__actions">
                <button className={`adm-pill ${item.is_published ? 'is-on' : ''}`} onClick={() => togglePublish(item)}>
                  {item.is_published ? 'Published' : 'Hidden'}
                </button>
                {def.files && (
                  <FileControls
                    item={item}
                    onError={fail}
                    onChange={u => { setItems(list => list?.map(i => (i.id === u.id ? u : i)) ?? null); toast('Certificate file updated') }}
                  />
                )}
                <button className="adm-btn adm-btn--ghost" onClick={() => setEditing({ ...(item as unknown as Draft) })}>Edit</button>
                {confirmId === item.id ? (
                  <>
                    <button className="adm-btn adm-btn--danger" onClick={() => remove(item.id)}>Confirm</button>
                    <button className="adm-btn adm-btn--ghost" onClick={() => setConfirmId(null)}>Keep</button>
                  </>
                ) : (
                  <button className="adm-btn adm-btn--ghost" onClick={() => setConfirmId(item.id)}>Delete</button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {editing && <Editor key={String(editing.id ?? 'new')} def={def} initial={editing} onCancel={() => setEditing(null)} onSave={save} />}
    </>
  )
}
