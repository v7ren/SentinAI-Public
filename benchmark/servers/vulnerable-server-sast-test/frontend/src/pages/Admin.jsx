import { useState } from 'react'
import { API } from '../App'

export default function Admin() {
  const [pingHost, setPingHost] = useState('127.0.0.1')
  const [pingResult, setPingResult] = useState('')
  const [fetchUrl, setFetchUrl] = useState('')
  const [fetchResult, setFetchResult] = useState('')
  const [logFile, setLogFile] = useState('app.log')
  const [logResult, setLogResult] = useState('')
  const [reportTpl, setReportTpl] = useState('Report: {{ title }}')
  const [reportResult, setReportResult] = useState('')
  const [pickleB64, setPickleB64] = useState('')

  const runPing = async () => {
    const res = await fetch(`${API}/api/ping?host=${encodeURIComponent(pingHost)}`)
    const text = await res.text()
    setPingResult(text)
  }

  const runFetch = async () => {
    const res = await fetch(`${API}/api/fetch?url=${encodeURIComponent(fetchUrl)}`)
    const data = await res.json()
    setFetchResult(JSON.stringify(data, null, 2))
  }

  const runLogs = async () => {
    const res = await fetch(`${API}/api/logs?file=${encodeURIComponent(logFile)}`)
    setLogResult(await res.text())
  }

  const runReport = async () => {
    const res = await fetch(`${API}/api/report/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ template: reportTpl, title: 'Test' }),
    })
    const data = await res.json()
    setReportResult(data.report || data.error || '')
  }

  const sendPickle = async () => {
    const body = Uint8Array.from(atob(pickleB64 || 'gAJ9'), (c) => c.charCodeAt(0))
    const res = await fetch(`${API}/api/config/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/octet-stream' },
      body,
    })
    const data = await res.json()
    setReportResult(JSON.stringify(data))
  }

  return (
    <div className="container">
      <h1>Admin / SAST test triggers</h1>
      <div className="card">
        <h3>Ping (command injection)</h3>
        <input value={pingHost} onChange={(e) => setPingHost(e.target.value)} placeholder="Host" />
        <button onClick={runPing}>Ping</button>
        <pre>{pingResult || '—'}</pre>
      </div>
      <div className="card">
        <h3>Fetch URL (SSRF)</h3>
        <input value={fetchUrl} onChange={(e) => setFetchUrl(e.target.value)} placeholder="http://..." style={{ width: 360 }} />
        <button onClick={runFetch}>Fetch</button>
        <pre>{fetchResult || '—'}</pre>
      </div>
      <div className="card">
        <h3>Logs (command injection)</h3>
        <input value={logFile} onChange={(e) => setLogFile(e.target.value)} placeholder="app.log" />
        <button onClick={runLogs}>Get logs</button>
        <pre>{logResult || '—'}</pre>
      </div>
      <div className="card">
        <h3>Report template (SSTI)</h3>
        <textarea value={reportTpl} onChange={(e) => setReportTpl(e.target.value)} rows={3} style={{ width: '100%' }} />
        <button onClick={runReport}>Generate</button>
        <pre>{reportResult || '—'}</pre>
      </div>
      <div className="card">
        <h3>Config import (pickle)</h3>
        <input value={pickleB64} onChange={(e) => setPickleB64(e.target.value)} placeholder="base64 pickle payload" style={{ width: '100%' }} />
        <button onClick={sendPickle}>Send</button>
      </div>
    </div>
  )
}
