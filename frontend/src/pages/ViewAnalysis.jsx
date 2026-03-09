import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api.js'
import Layout from '../components/Layout.jsx'
import MarkdownRenderer from '../components/MarkdownRenderer.jsx'

export default function ViewAnalysis() {
  const { id } = useParams()
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getAnalysis(id)
      .then(setAnalysis)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  return (
    <Layout>
      <div className="page-header">
        <Link to="/dashboard" className="btn btn-secondary btn-sm">← Dashboard</Link>
      </div>

      {loading && (
        <div className="text-center" style={{ padding: '48px 0' }}>
          <span className="spinner" />
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {analysis && (
        <>
          <div className="card mb-4" style={{ background: 'var(--primary-light)', borderColor: '#bfdbfe' }}>
            <div className="text-sm text-muted mb-2">Consulta</div>
            <p style={{ fontWeight: 500 }}>{analysis.query}</p>
            <div className="text-sm text-muted mt-2">
              {new Date(analysis.created_at).toLocaleString('es-CO')}
            </div>
          </div>
          <div className="card">
            <MarkdownRenderer content={analysis.analysis} />
          </div>
        </>
      )}
    </Layout>
  )
}
