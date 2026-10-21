import type { FieldDef } from './fields'

type Value = string | number | boolean | string[] | undefined

interface Props { field: FieldDef; value: Value; onChange: (v: Value) => void }

export default function FieldInput({ field, value, onChange }: Props) {
  const id = `f-${field.name}`
  const type = field.type ?? 'text'
  const cls = `adm-field ${field.wide ? 'adm-field--wide' : ''}`

  if (type === 'bool') {
    return (
      <label className={`${cls} adm-field--check`} htmlFor={id}>
        <input id={id} type="checkbox" checked={Boolean(value)} onChange={e => onChange(e.target.checked)} />
        <span>{field.label}</span>
      </label>
    )
  }

  let control
  if (type === 'textarea') {
    control = <textarea id={id} rows={4} value={String(value ?? '')} required={field.required} onChange={e => onChange(e.target.value)} />
  } else if (type === 'lines') {
    control = <textarea id={id} rows={6} value={Array.isArray(value) ? value.join('\n') : String(value ?? '')} onChange={e => onChange(e.target.value.split('\n'))} />
  } else if (type === 'tags') {
    control = <input id={id} value={Array.isArray(value) ? value.join(', ') : String(value ?? '')} onChange={e => onChange(e.target.value.split(','))} />
  } else if (type === 'select') {
    control = (
      <select id={id} value={String(value ?? '')} onChange={e => onChange(e.target.value)}>
        {field.options?.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    )
  } else if (type === 'number') {
    control = <input id={id} type="number" value={Number(value ?? 0)} onChange={e => onChange(Number(e.target.value))} />
  } else {
    control = <input id={id} value={String(value ?? '')} required={field.required} onChange={e => onChange(e.target.value)} />
  }

  return (
    <div className={cls}>
      <label htmlFor={id}>{field.label}{field.required && <b> *</b>}</label>
      {control}
      {field.help && <small>{field.help}</small>}
    </div>
  )
}

/** Normalise list-ish values before sending to the API. */
export function cleanForSubmit(fields: FieldDef[], data: Record<string, Value>) {
  const out: Record<string, Value> = { ...data }
  for (const f of fields) {
    if ((f.type === 'tags' || f.type === 'lines') && Array.isArray(out[f.name])) {
      out[f.name] = (out[f.name] as string[]).map(s => s.trim()).filter(Boolean)
    }
  }
  return out
}
