import { useState } from 'react'
import { API } from '../App'

export default function Export() {
  const [orderIds, setOrderIds] = useState('1,2,3')
  const [csv, setCsv] = useState('')
  const [redirectTo, setRedirectTo] = useState('')

  const exportCsv = async () => {
    const res = await fetch(`${API}/api/export/csv?order_ids=${encodeURIComponent(orderIds)}`)
    setCsv(await res.text())
  }

  const doRedirect = () => {
    if (redirectTo) {
      window.location.href = redirectTo
    }
  }

  return (
    <div className="container">
      <h1>Export</h1>
      <div className="card">
        <h3>CSV export (SQLi in order_ids)</h3>
        <input value={orderIds} onChange={(e) => setOrderIds(e.target.value)} placeholder="1,2,3" style={{ width: 200 }} />
        <button onClick={exportCsv}>Export CSV</button>
        <pre>{csv || '—'}</pre>
      </div>
      <div className="card">
        <h3>Open redirect</h3>
        <input value={redirectTo} onChange={(e) => setRedirectTo(e.target.value)} placeholder="https://evil.com" style={{ width: 360 }} />
        <button onClick={doRedirect}>Go</button>
      </div>
    </div>
  )
}
