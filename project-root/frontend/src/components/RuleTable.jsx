import React, { useEffect, useState } from 'react'

export default function RuleTable() {
  const [rules, setRules] = useState([])
  const [form, setForm] = useState({ id: '', condition: '', action: '' })

  const load = async () => {
    const res = await fetch('/api/rules')
    setRules(await res.json())
  }

  useEffect(() => { load() }, [])

  const add = async () => {
    const body = { id: Number(form.id), condition: form.condition, action: form.action }
    await fetch('/api/rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    setForm({ id: '', condition: '', action: '' })
    load()
  }

  const del = async (id) => {
    await fetch(`/api/rules/${id}`, { method: 'DELETE' })
    load()
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input placeholder="id" value={form.id} onChange={e => setForm({ ...form, id: e.target.value })} />
        <input placeholder="condition" style={{ flex: 1 }} value={form.condition} onChange={e => setForm({ ...form, condition: e.target.value })} />
        <input placeholder="action" style={{ flex: 1 }} value={form.action} onChange={e => setForm({ ...form, action: e.target.value })} />
        <button onClick={add} disabled={!form.id || !form.condition || !form.action}>Add</button>
        <a href="/api/export">Export CSV</a>
      </div>
      <table border="1" cellPadding="6" cellSpacing="0">
        <thead><tr><th>id</th><th>condition</th><th>action</th><th></th></tr></thead>
        <tbody>
          {rules.map(r => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.condition}</td>
              <td>{r.action}</td>
              <td><button onClick={() => del(r.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
