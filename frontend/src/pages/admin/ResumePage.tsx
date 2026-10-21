import { useEffect, useRef, useState } from 'react'
import { adminApi, resumeUrl } from '../../api/client'
import type { ResumeInfo } from '../../api/types'
import { useToast } from '../../context/ToastContext'

export default function ResumePage() {
  const [info, setInfo] = useState<ResumeInfo | null>(null)
  const [busy, setBusy] = useState(false)
  const [confirm, setConfirm] = useState(false)
  const input = useRef<HTMLInputElement>(null)
  const toast = useToast()

  useEffect(() => { adminApi.resume().then(setInfo).catch(() => {}) }, [])

  const upload = async (file?: File) => {
    if (!file) return
    setBusy(true)
    try { setInfo(await adminApi.uploadResume(file)); toast('Résumé updated') }
    catch (e) { toast(e instanceof Error ? e.message : 'Upload failed', 'error') }
    finally { setBusy(false); if (input.current) input.current.value = '' }
  }
  const remove = async () => {
    await adminApi.deleteResume(); setInfo({ available: false }); setConfirm(false); toast('Résumé removed')
  }

  return (
    <>
      <div className="adm-head"><div><h1>Résumé</h1><p className="adm-muted">The PDF behind every “Download résumé” button.</p></div></div>
      <div className="adm-card adm-section">
        {info?.available ? (
          <p>Current file: <b>{((info.size ?? 0) / 1024).toFixed(0)} KB</b>, updated {info.updated_at && new Date(info.updated_at).toLocaleString()}</p>
        ) : <p className="adm-muted">No résumé uploaded — the download buttons are hidden on the site.</p>}
        <div
          className="adm-drop"
          onDragOver={e => e.preventDefault()}
          onDrop={e => { e.preventDefault(); upload(e.dataTransfer.files[0]) }}
          onClick={() => input.current?.click()}
        >
          {busy ? 'Uploading…' : 'Drop a PDF here or click to choose'}
          <input ref={input} type="file" accept="application/pdf" hidden onChange={e => upload(e.target.files?.[0])} />
        </div>
        <div className="adm-actions adm-actions--left">
          {info?.available && <a className="adm-btn adm-btn--ghost" href={`${resumeUrl}?t=${info.updated_at}`} target="_blank" rel="noreferrer">Preview ↗</a>}
          {info?.available && (confirm
            ? <><button className="adm-btn adm-btn--danger" onClick={remove}>Confirm delete</button><button className="adm-btn adm-btn--ghost" onClick={() => setConfirm(false)}>Keep</button></>
            : <button className="adm-btn adm-btn--ghost" onClick={() => setConfirm(true)}>Delete</button>)}
        </div>
      </div>
    </>
  )
}
