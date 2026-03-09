import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useUser } from '../App.jsx'
import Layout from '../components/Layout.jsx'

export default function Dashboard() {
  const { user } = useUser()
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getUserAnalyses(user.user_id)
      .then(data => setAnalyses(data.analyses))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [user.user_id])

  async function handleDelete(e, id) {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('¿Eliminar este análisis?')) return
    try {
      await api.deleteAnalysis(id)
      setAnalyses(prev => prev.filter(a => a.analysis_id !== id))
    } catch (err) {
      alert(err.message)
    }
  }

  return (
    <Layout>
      <div className="page-header">
        <h1 className="page-title">Mis análisis</h1>
        <Link to="/analysis/new" className="btn btn-primary">+ Nuevo análisis</Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="text-center text-muted" style={{ padding: '48px 0' }}>
          <span className="spinner" />
        </div>
      ) : analyses.length === 0 ? (
        <div className="card text-center" style={{ padding: '48px 24px' }}>
          <p className="text-muted mb-4">No tienes análisis aún.</p>
          <Link to="/analysis/new" className="btn btn-primary">Crear primer análisis</Link>
        </div>
      ) : (
        <div className="analysis-list">
          {analyses.map(a => (
            <Link key={a.analysis_id} to={`/analysis/${a.analysis_id}`} className="analysis-item">
              <div>
                <div className="analysis-item-query">{a.query}</div>
                <div className="analysis-item-meta">
                  {new Date(a.created_at).toLocaleString('es-CO')}
                </div>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={e => handleDelete(e, a.analysis_id)}
              >
                Eliminar
              </button>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  )
}
