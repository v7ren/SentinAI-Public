import { useEffect, useState } from 'react'

export default function Home() {
  const [banner, setBanner] = useState('')
  const [widget, setWidget] = useState('')

  // VULN: DOM XSS via location.hash
  useEffect(() => {
    const hash = window.location.hash.slice(1)
    if (hash) {
      const el = document.getElementById('banner-display')
      if (el) el.innerHTML = decodeURIComponent(hash)
    }
  }, [])

  // VULN: Prototype pollution via URL ?config={"__proto__":{"admin":true}}
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const config = params.get('config')
    if (config) {
      try {
        const parsed = JSON.parse(config)
        const defaults = { theme: 'dark', lang: 'en' }
        const merged = { ...defaults, ...parsed }
        setWidget(JSON.stringify(merged))
      } catch (e) {
        console.error(e)
      }
    }
  }, [])

  // VULN: postMessage without origin check + eval
  useEffect(() => {
    const handler = (event) => {
      if (event.data?.type === 'run') {
        try {
          const result = eval(event.data.code)
          event.source?.postMessage({ result }, '*')
        } catch (e) {
          event.source?.postMessage({ error: String(e) }, '*')
        }
      }
      if (event.data?.type === 'setBanner') {
        setBanner(event.data.text)
      }
    }
    window.addEventListener('message', handler)
    return () => window.removeEventListener('message', handler)
  }, [])

  return (
    <div className="container">
      <h1>SAST Test App</h1>
      <p>Intentional vulnerabilities for scanner benchmarking. Do not use in production.</p>
      <div className="card">
        <h3>Banner (hash)</h3>
        <div id="banner-display" />
      </div>
      <div className="card">
        <h3>Widget (postMessage / config)</h3>
        {widget && <pre>{widget}</pre>}
        {banner && <div dangerouslySetInnerHTML={{ __html: `Banner: ${banner}` }} />}
      </div>
    </div>
  )
}
