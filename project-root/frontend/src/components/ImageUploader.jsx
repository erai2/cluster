import React, { useState } from 'react'

export default function ImageUploader() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch('/api/upload-image', { method: 'POST', body: fd })
    setResult(await res.json())
  }

  return (
    <form onSubmit={onSubmit}>
      <input type="file" accept="image/*" onChange={e => setFile(e.target.files?.[0] ?? null)} />
      <button type="submit" disabled={!file}>Upload</button>
      {result && (
        <pre style={{ background: '#f6f8fa', padding: 12, marginTop: 12 }}>
{JSON.stringify(result, null, 2)}
        </pre>
      )}
    </form>
  )
}
