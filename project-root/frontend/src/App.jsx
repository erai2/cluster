import React, { useEffect, useState } from 'react'
import FileUploader from './components/FileUploader.jsx'
import RuleTable from './components/RuleTable.jsx'

export default function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    fetch('/api/health').then(r => r.json()).then(setHealth).catch(() => setHealth(null))
  }, [])

  return (
    <div style={{ padding: 16, maxWidth: 960, margin: '0 auto' }}>
      <h1>HCJ Demo</h1>
      <p>Backend: {health ? `OK (${health.ts})` : 'connecting...'}</p>
      <section>
      <h2>Upload File</h2>
      <FileUploader />
      </section>
      <section>
        <h2>Rules</h2>
        <RuleTable />
      </section>
    </div>
  )
}
